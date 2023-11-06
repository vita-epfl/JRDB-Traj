import torch


class InputEmbedding(torch.nn.Module):
    """Linear embedding, ReLU non-linearity, input scaling.

    Input scaling is important for ReLU activation combined with the initial
    bias distribution. Otherwise some units will never be active.
    """
    def __init__(self, input_dim, embedding_dim, scale, use_tags=True):
        super(InputEmbedding, self).__init__()
        self.embedding_dim = embedding_dim
        self.scale = scale
        self.use_tags = use_tags

        linear_embedding_dim = self.embedding_dim
        if use_tags:
            linear_embedding_dim -= 3
        self.input_embeddings = torch.nn.Sequential(
            torch.nn.Linear(input_dim, linear_embedding_dim),
            torch.nn.ReLU(),
        )

    def forward(self, vel):
        if self.use_tags:
            return torch.cat([
                self.input_embeddings(vel * self.scale),
                torch.zeros(vel.size(0),3, device=vel.device),
            ], dim=1)
        return self.input_embeddings(vel * self.scale)


class Hidden2Normal(torch.nn.Module):
    def __init__(self, hidden_dim):
        super(Hidden2Normal, self).__init__()
        self.linear = torch.nn.Linear(hidden_dim, 3)

    def forward(self, hidden_state):
        normal = self.linear(hidden_state)
        normal[:,2] = torch.sigmoid(normal[:,2])

        return normal
