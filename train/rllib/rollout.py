if hasattr(agent, "local_evaluator"):
        env = agent.local_evaluator.env
    else:
        env = ModelCatalog.get_preprocessor_as_wrapper(gym.make(args.env))
    if args.out is not None:
        rollouts = []
    steps = 0
    while steps < (num_steps or steps + 1):
        if args.out is not None:
            rollout = []
        state = env.reset()
        done = False
        reward_total = 0.0
        while not done and steps < (num_steps or steps + 1):
            action = agent.compute_action(state)
            next_state, reward, done, _ = env.step(action)
            reward_total += reward
            if not args.no_render:
                env.render()
            if args.out is not None:
                rollout.append([state, action, next_state, reward, done])
            steps += 1
            state = next_state
        if args.out is not None:
            rollouts.append(rollout)
        print("Episode reward", reward_total)
    if args.out is not None:
        pickle.dump(rollouts, open(args.out, "wb"))