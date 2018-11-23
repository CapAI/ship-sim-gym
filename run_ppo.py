# What if we use a smarter agent ...?

# Baselines contains implementations of all the common RL algorithms ..

#!/usr/bin/env python3

import gym

# This will add it to the registry!
import ship_gym

from mpi4py import MPI
from baselines.common import set_global_seeds
from baselines import bench
import os.path as osp
from baselines import logger
from baselines.common.atari_wrappers import make_atari, wrap_deepmind
from baselines.common.cmd_util import atari_arg_parser

def train(num_timesteps, seed):
    from baselines.ppo1 import pposgd_simple, cnn_policy
    import baselines.common.tf_util as U
    
    rank = MPI.COMM_WORLD.Get_rank()
    sess = U.single_threaded_session()
    sess.__enter__()
    if rank == 0:
        logger.configure()
    else:
        logger.configure(format_strs=[])
    workerseed = seed + 10000 * MPI.COMM_WORLD.Get_rank() if seed is not None else None
    set_global_seeds(workerseed)

    def policy_fn(name, ob_space, ac_space): #pylint: disable=W0613
        return cnn_policy.CnnPolicy(name=name, ob_space=ob_space, ac_space=ac_space)

    # env = ShipEnv(speed=1, fps=10)

    env = gym.make('ShipSim-v0')
    env = bench.Monitor(env, logger.get_dir() and
        osp.join(logger.get_dir(), str(rank)))
    env.seed(workerseed)

    pposgd_simple.learn(env, policy_fn,
        max_timesteps=int(num_timesteps * 1.1),
        timesteps_per_actorbatch=256,
        clip_param=0.2, entcoeff=0.01,
        optim_epochs=4, optim_stepsize=1e-3, optim_batchsize=64,
        gamma=0.99, lam=0.95,
        schedule='linear'
    )
    env.close()

def main():
    train(1000, 0)

main()
