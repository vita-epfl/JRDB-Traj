import torch

class L2Loss(torch.nn.Module):
    """L2 Loss (deterministic version of PredictionLoss)

    This Loss penalizes only the primary trajectories
    """
    def __init__(self, keep_batch_dim=False):
        super(L2Loss, self).__init__()
        self.loss = torch.nn.MSELoss(reduction='none')
        self.keep_batch_dim = keep_batch_dim
        self.loss_multiplier = 100

    def col_loss(self, primary, neighbours, batch_split, gamma=2.0):
        """
        Penalizes model when primary pedestrian prediction comes close
        to the neighbour predictions
        primary: Tensor [pred_length, 1, 2]
        neighbours: Tensor [pred_length, num_neighbours, 2]
        """

        neighbours[neighbours != neighbours] = -1000
        exponential_loss = 0.0
        for (start, end) in zip(batch_split[:-1], batch_split[1:]):
            batch_primary = primary[:, start:start+1]
            batch_neigh = neighbours[:, start:end]
            distance_to_neigh = torch.norm(batch_neigh - batch_primary, dim=2)
            mask_far = (distance_to_neigh < 0.25).detach()
            distance_to_neigh = -gamma * distance_to_neigh * mask_far
            exponential_loss += distance_to_neigh.exp().sum()
        return exponential_loss.sum()

    def forward(self, inputs, targets, batch_split):
        ## Extract primary pedestrians
        targets = targets.transpose(0, 1)
        targets = targets[batch_split[:-1]]
        targets = targets.transpose(0, 1)
        inputs = inputs.transpose(0, 1)
        inputs = inputs[batch_split[:-1]]
        inputs = inputs.transpose(0, 1)

        mask_gt = ~torch.isnan(targets[:,:,0])
        mask_pred = ~torch.isnan(inputs[:,:,0])
        mask = mask_pred*mask_gt
  
        loss_vis = self.loss(inputs[mask], targets[mask])
        if inputs[~mask].size(0) == 0:
            loss = loss_vis
        else:
            loss_invis = self.loss(inputs[~mask][:,-1], targets[~mask][:,-1])
            loss_invis = torch.cat((loss_invis.unsqueeze(1),torch.zeros(loss_invis.size(0),2).to(loss_invis.device)),dim=1)
            loss = torch.cat((loss_vis, loss_invis),dim=0)

        ## Used in variety loss (SGAN)
        if self.keep_batch_dim:
            return loss.mean(dim=0).mean(dim=1) * self.loss_multiplier

        return torch.mean(loss) * self.loss_multiplier

