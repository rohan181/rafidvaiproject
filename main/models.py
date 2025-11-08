from django.db import models

# Create your models here.


from django.db import models

class BoronDoping(models.Model):
    nb = models.FloatField(verbose_name="Substrate Concentration (cm⁻³)", default=1e15)
    q = models.FloatField(verbose_name="Ion Dose Charge (C)", default=1e12)
    sig = models.FloatField(verbose_name="Sigma (Straggle Parameter)", default=107e-8)
    rp = models.FloatField(verbose_name="RP (Range Parameter in cm)", default=326e-8)
    tox = models.FloatField(verbose_name="Oxide thickness (cm)", default=0.5e-5)