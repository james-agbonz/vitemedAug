import os
import torch.nn as nn
from transformers import BlipForConditionalGeneration, AutoProcessor
# Disable parallelism for tokenizers
os.environ["TOKENIZERS_PARALLELISM"] = "false"


def model_init_func(**model_init_kwargs):
    return MyBlipForConditionalGeneration(**model_init_kwargs)


def model_fine_tune_func(model, output_features):
    return model


# Define an Vision Encoder-Decoder module for the Transformer architecture

class MyBlipForConditionalGeneration(nn.Module):
    def __init__(self):
        super(MyBlipForConditionalGeneration, self).__init__()
        processor = AutoProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base")
        self.model = model
        self.processor = processor

    def forward(self, _x, _y):
        raise NotImplementedError(
            'forward method is no need to be implemented')

    def get_output_loss(self, _x, _y, loss_fn):
        encoding = self.processor(
            images=_x,
            text=_y,
            padding="max_length",
            return_tensors="pt",
            do_rescale=False
        )

        outputs = self.model(
            input_ids=encoding["input_ids"].to(_x.device),
            attention_mask=encoding["attention_mask"].to(_x.device),
            pixel_values=encoding["pixel_values"].to(_x.device),
            labels=encoding["input_ids"].to(_x.device)
        )

        return outputs, outputs.loss

    def inference(self, _x):
        inputs = self.processor(
            images=_x,
            return_tensors="pt",
            do_rescale=False
        )
        pixel_values = inputs.pixel_values

        generated_ids = self.model.generate(
            pixel_values=pixel_values,
            max_length=50
        )
        generated_caption = self.processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]

        return generated_caption
