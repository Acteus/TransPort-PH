import sys
sys.path.insert(0, '/Users/gdullas/Desktop/Projects/Neural-Network-Projects/TransPort-PH/venv/lib/python3.10/site-packages')

# Check pytorch-forecasting's lightning import
from pytorch_forecasting.models.base_model import BaseModel
from pytorch_forecasting import TemporalFusionTransformer

# Check what Trainer expects
from pytorch_lightning import Trainer, LightningModule as PL_LightningModule
from lightning.pytorch import LightningModule as Lightning_LightningModule

print("BaseModel MRO:")
for cls in BaseModel.__mro__[:15]:
    print(f"  {cls.__module__}.{cls.__name__}")

print("\nChecking isinstance:")
# Create a dummy model instance
print(f"BaseModel is subclass of PL_LightningModule: {issubclass(BaseModel, PL_LightningModule)}")
print(f"BaseModel is subclass of Lightning_LightningModule: {issubclass(BaseModel, Lightning_LightningModule)}")

print("\nModule paths:")
print(f"pytorch_lightning.LightningModule: {PL_LightningModule.__module__}")
print(f"lightning.pytorch.LightningModule: {Lightning_LightningModule.__module__}")
