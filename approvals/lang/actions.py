def run_to_interrupt_or_completion(graph, inputs, config):
    result = graph.invoke(inputs, config)
    snapshot = graph.get_state(config)

    if snapshot.next:
        # There was an interrupt
        print("interrupt found")
        print(snapshot.next)

        # Save the snapshot
        checkpoint_id = snapshot.config["configurable"]["checkpoint_id"]

        print(f"Snapshot saved with checkpoint_id: {checkpoint_id}")
        return (None, snapshot)
    else:
        # We have a final result
        print("final result")
        print(result["messages"][-1].content)
        return (result, snapshot)
