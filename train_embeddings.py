import wandb, os
import pytorch_lightning
from pytorch_lightning.callbacks.model_checkpoint import ModelCheckpoint
from pytorch_lightning.loggers import WandbLogger
from datasets import *
from models import *
from models.EmbeddingsModel import EmbeddingsModel



os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]="1"

config = {
    "embeddings_size": int(os.environ.get("embeddings_size", 256)),
    "learning_rate":   float(os.environ.get("learning_rate", 0.0001)),
    "epochs":          int(os.environ.get("epochs", 300)),
    "dropout":         float(os.environ.get("dropout", 0.3)),
    "regularization":  float(os.environ.get("regularization", 0.1)),
    "batch_size":      int(os.environ.get("batch_size", 1024)),
    "val_batch_size":  int(os.environ.get("val_batch_size", 8)),
    "decoder":         str(os.environ.get("decoder", 'DistMultDecoder')),
    'device': 'cuda'
}
    

if __name__ == '__main__':
    
    data  = MetaQaEmbeddings(config['batch_size'], config['val_batch_size'])
    model = EmbeddingsModel(data.ds.n_embeddings, data.ds.n_relations, config)
        
    # Initialize data and model for pre-training
    
    wandb.init( project="metaqa", reinit=True)
    wandb_logger = WandbLogger(log_model=True)
    
                
    embeddings_checkpoint_callback = ModelCheckpoint(
        dirpath='checkpoints/embeddings/',
        filename=f'{model.cname()}'+'|{epoch}|{hit@10}'  
        )  
    
    trainer = pytorch_lightning.Trainer( 
        ** {'gpus':1, 'auto_select_gpus': True } if config['device'] == 'cuda' else {},
        callbacks=[embeddings_checkpoint_callback],
        logger= wandb_logger, 
        log_every_n_steps=1,
        check_val_every_n_epoch=50,
        limit_val_batches=1024,
        max_epochs=config['epochs'])
    
    trainer.fit(model, data)
    wandb.finish()

