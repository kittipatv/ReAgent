#!/usr/bin/env python3

from typing import Dict, List, Type

import torch
from reagent import types as rlt
from reagent.core.dataclasses import dataclass, field
from reagent.models.base import ModelBase, SequentialWithDimensions
from reagent.models.dqn import FullyConnectedDQN
from reagent.models.fully_connected_network import FullyConnectedNetwork
from reagent.models.id_list_joiner import IdListJoiner
from reagent.net_builder.discrete_dqn_net_builder import DiscreteDQNWithIdListNetBuilder
from reagent.parameters import NormalizationParameters, param_hash


@dataclass
class FullyConnectedWithEmbedding(DiscreteDQNWithIdListNetBuilder):
    __hash__ = param_hash

    sizes: List[int] = field(default_factory=lambda: [256, 128])
    activations: List[str] = field(default_factory=lambda: ["relu", "relu"])
    embedding_dim: int = 64
    dropout_ratio: float = 0.0

    def __post_init_post_parse__(self):
        super().__init__()
        assert len(self.sizes) == len(self.activations), (
            f"Must have the same numbers of sizes and activations; got: "
            f"{self.sizes}, {self.activations}"
        )

    def build_q_network(
        self,
        state_feature_config: rlt.ModelFeatureConfig,
        state_normalization_parameters: Dict[int, NormalizationParameters],
        output_dim: int,
    ) -> ModelBase:
        state_dim = self._get_input_dim(state_normalization_parameters)
        id_list_joiner = IdListJoiner(
            state_feature_config, state_dim, self.embedding_dim
        )
        embedding = FullyConnectedNetwork(
            layers=[id_list_joiner.output_dim()] + self.sizes,
            activations=self.activations,
            dropout_ratio=self.dropout_ratio,
        )
        return FullyConnectedDQN(
            action_dim=output_dim, feature_extractor=id_list_joiner, embedding=embedding
        )