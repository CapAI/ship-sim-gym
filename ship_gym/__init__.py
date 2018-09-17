from gym.envs.registration import register

register(
    id='ShipSim-v0',
    entry_point='ship_gym.envs.ship_sim_env:ShipEnv',
)

print("Registered ship sim gym env")
# register(
#     id='ShipSimExtraHard-v0',
#     entry_point='gym_foo.envs:ShipExtraHardEnv',
# )