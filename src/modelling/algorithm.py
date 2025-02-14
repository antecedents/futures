"""Module algorithm.py"""
import pandas as pd
import pymc


# noinspection PyUnresolvedReferences
class Algorithm:
    """
    The multi-level algorithm
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def exc(n_lags, n_eqs, df, group_field, prior_checks=True):
        """

        :return:
        """

        cols = [col for col in df.columns if col != group_field]
        coords = {"lags": np.arange(n_lags) + 1,
                  "equations": cols
                  }

        groups = df[group_field].unique()

        priors = {
            "noise": {"sigma": 1}
        }

        with pymc.Model(coords=coords) as model:

            ## Hierarchical Priors
            alpha_hat_location = pymc.Normal("alpha_hat_location", 0, 0.1)
            alpha_hat_scale = pymc.InverseGamma("alpha_hat_scale", 3, 0.5)
            beta_hat_location = pymc.Normal("beta_hat_location", 0, 0.1)
            beta_hat_scale = pymc.InverseGamma("beta_hat_scale", 3, 0.5)


            for grp in groups:

                df_grp = df[df[group_field] == grp][cols]
                z_scale_beta = pymc.InverseGamma(f"z_scale_beta_{grp}", 3, 0.5)
                z_scale_alpha = pymc.InverseGamma(f"z_scale_alpha_{grp}", 3, 0.5)
                lag_coefs = pymc.Normal(
                    f"lag_coefs_{grp}",
                    mu=beta_hat_location,
                    sigma=beta_hat_scale * z_scale_beta,
                    dims=["equations", "lags"],
                )
                alpha = pymc.Normal(
                    f"alpha_{grp}",
                    mu=alpha_hat_location,
                    sigma=alpha_hat_scale * z_scale_alpha,
                    dims=("equations",)
                )

                betaX = calc_ar_step(lag_coefs, n_eqs, n_lags, df_grp)
                betaX = pymc.Deterministic(f"betaX_{grp}", betaX)
                mean = alpha + betaX

                ## This is an alternative likelihood that can recover sensible estimates of the coefficients
                ## But lacks the multivariate correlation between the timeseries.
                sigma = pymc.HalfNormal(f'sigma_{grp}', sigma=priors["noise"]["sigma"], dims=["equations"])
                pymc.Normal(f'likelihood_{grp}', mu=mean, sigma=sigma, observed=df_grp.values[n_lags:])


            if prior_checks:
                idata = pymc.sample_prior_predictive()
                return model, idata
            else:
                idata = pymc.sample_prior_predictive()
                idata.extend(pymc.sampling.jax.sample_blackjax_nuts(2000, random_seed=100))
                idata.extend(pymc.sample_posterior_predictive(idata))

        return model, idata
