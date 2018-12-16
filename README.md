# Ship Sim Gym

Low-fidelity high-performance ship simulator built with pygame / pymunk with OpenAI gym wrapper and example scripts for stable-baselines and rllib for training RL agents.

This gym and the accompanying scripts allow you to quickly iterate over different ideas	

For questions / comments: do not hesitate to do so via the issues or a direct PM to [gerardsimons](https://github.com/gerardsimons/).

## Requirements

Python 3.6 is required. Make sure you are **not** using Python 3.7. It's not supported by ray / rllib and a few others at moment of writing.

### Pygame / Pymunk

The game is built with pygame and pymunk. pygame is a library that allows for creating windows and drawing primivites. Pymunk is needed for the physics. Both should be pip installable.

### Stable Baselines

[stable-baselines](https://github.com/hill-a/stable-baselines) has specific prerequisites listed in the README, make sure you meet those before continuing.

### RLlib 

`pip install ray[rllib]` should do. See specific version in requirements.txt

If you get an issue like this:

```
redis.exceptions.DataError: Invalid input of type: 'NoneType'. Convert to a byte, string or number first.
```

Revert back to Redis 2:

`pip install -U redis==2.10.6`

## Usage

Easiest thing is to run the jupyter notebook. Even though the code is mostly just imports from existing scripts it explains quite a bit in the Markdown cells. 

Run from the repo root:

`jupyter notebook notebooks`

NOTE: It seems some of the code doesn't do to well in a notebook cell. If you prefer you can also run the scripts in train manually by calling them as modules. For example to run the PPO trainer of RLLib do:

`python -m train.rllib.ppo`

## Contributing

Again feel free to discuss ideas or propose new features via the issues tab!

If you have an idea for a feature, feel free to create your own feature branch:

`git checkout -b feature/<feature_name>`

Once finished, you can do a pull request. 