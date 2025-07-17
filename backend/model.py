import torch
import numpy as np
import pandas as pd
import onnxruntime as ort

class InferenceModel:
    def __init__(self, onnx_path="astgcn_v2.onnx", device="cpu"):
        providers = (["CUDAExecutionProvider","CPUExecutionProvider"]
                     if device.startswith("cuda") else ["CPUExecutionProvider"])
        self.sess = ort.InferenceSession(onnx_path, providers=providers)

        # Inspect the ONNX inputs
        inputs = self.sess.get_inputs()
        names = [inp.name for inp in inputs]
        if len(names) == 2:
            # graph expects [X, edge_index]
            self.input_name, self.edge_name = names
            self.need_edge = True
        elif len(names) == 1:
            # graph only expects [X], edge_index is built-in
            self.input_name = names[0]
            self.edge_name = None
            self.need_edge = False
        else:
            raise RuntimeError(f"Unexpected number of inputs in ONNX model: {len(names)}")

        self.output_name = self.sess.get_outputs()[0].name

    def forecast(self, X: torch.Tensor, edge_index: torch.Tensor = None) -> torch.Tensor:
        """
        X: [B, N, 1, seq_len]
        edge_index: [2, E] (only required if the ONNX session expects it)
        """
        Xn = X.cpu().numpy().astype(np.float32)
        feed = {self.input_name: Xn}

        if self.need_edge:
            if edge_index is None:
                raise ValueError("This model requires edge_index, but none was given.")
            En = edge_index.cpu().numpy().astype(np.int64)
            feed[self.edge_name] = En

        out = self.sess.run([self.output_name], feed)[0]
        return torch.from_numpy(out)
