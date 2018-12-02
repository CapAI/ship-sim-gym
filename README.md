# ship-sim-gym

Extremely low-fidelity pygame / pymunk based Ship Simulator with OpenAI gym wrapper

## Installation

Make sure you are not using Python 3.7. It's not supported by ray / rllib and a few others at moment of writing.

## Stable Baselines

[stable-baselines](https://github.com/hill-a/stable-baselines) has specific prerequisites listed in the README.

## RLlib 

`pip install ray[rllib]` should do. See specific version in requirements.txt

If you get an issue like this:

```
redis.exceptions.DataError: Invalid input of type: 'NoneType'. Convert to a byte, string or number first.
```

Revert back to Redis 2:

`pip install -U redis==2.10.6`

You can try to do a pip install -r requirements.txt

Also see the requirements at each repo, especially stable-baselines has a few local ones.

PyGame instructions should be found separately onine

## Usage

training scripts are in `agents`.