from sentence_transformers import SentenceTransformer
import os


def check_path(config):
    if not os.path.exists(config.LOCAL_MODELS_PATH):
        
        os.makedirs(config.LOCAL_MODELS_PATH)
        
    else: return True

def check_model_exsits(config):
    model_dir = os.path.join(
                config.LOCAL_MODELS_PATH,
                config.MODEL_ID
            )
    if not os.path.exists(
        model_dir
    ):
        
        Model = SentenceTransformer(config.MODEL_ID)
        os.makedirs(
                    model_dir
                )
        Model.save_pretrained(model_dir)

    else:return True


