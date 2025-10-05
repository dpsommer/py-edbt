# py-edbt

Event-driven Behaviour Tree implemenation in Python. Based on [Agis et al., 2020](https://www.sciencedirect.com/science/article/abs/pii/S0957417420302815) and [Champandard and Dunstan, 2012](https://www.gameaipro.com/GameAIPro/GameAIPro_Chapter06_The_Behavior_Tree_Starter_Kit.pdf).

This library provides the building blocks for Behaviour Trees with dynamic "request handler" and "Blackboard Observer Decorator" (BOD) nodes. These allow agents to dynamically respond to local or world state changes, as well as receive and respond to events from other agents.

These dynamic components allow for the creation of connected agents that exhibit emergent group behaviour.

## Terms

| **Term**           | **Definition**                                                                                                           |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| **Behaviour Tree** |                                                                                                                          |
| **Condition**      | A typically binary evaluation of state used to determine whether or not a node is evaluated                              |
| **Tick**           | A tick can either refer to a game-clock tick (a single in-game frame/timespan) or the act of querying a node in the tree |
| **Agent/Actor**    | A non-player entity                                                                                                      |
| **Player**         | a user-controlled entity                                                                                                 |

## Agents

A behaviour tree is created to be associated with an agent - an in-game entity that can perform autonomous actions in response to internal and external state triggers. A town citizen, a bodyguard, or a non-player ally are all examples of agents that may act independently based on the game world around them and player decisions.

## Conditions and Abort Rules

## Nodes

A Behaviour Tree is made up of Behaviour nodes that define the actions an agent can take. On each tick, the tree is walked from the root, querying each child until a specific action is chosen to be executed. This selection process can depend on many factors, including the internal actor state, the player state, or the external world state.

Leaf nodes in the tree define behaviours: actions that are taken by the agent. These can range from simple (e.g. play an idle animation) to complex (e.g. call allies for help tracking down the player), and specify what the agent is doing at any given moment in-game.

Branch nodes define conditional paths for the agent to decide which action to take.

### Statuses

Each node returns one of either `SUCCESS`, `FAILURE`, or `RUNNING` as its current status. This status is then propagated back up the tree, ultimately resulting in a single overall status for the agent returned from the tree root. The dynamic elements of this implementation introduce a fourth `ABORTED` state that can be returned from children that are stopped mid-execution.

### Composite Nodes

Composite nodes are branch nodes with one or more children, ticking each in sequence and returning a result based on their aggregate status.

#### Sequencer

Sequencer nodes that tick each child sequentially, returning `SUCCESS` if and only if all children return `SUCCESS`. Otherwise, the first non-`SUCCESS` status is returned.

#### Selector

Selector nodes that tick each child sequentially, returning the first non-`FAILURE` status. If all children return `FAILURE`, the selector will return `FAILURE` as well.

#### Parallel

Parallel nodes that tick all children in parallel. These nodes can alternately be defined with a `SuccessPolicy` to return `SUCCESS` upon the success of a single child, or to require all children to respond successfully. In the latter mode, the Parallel node will continue to report `RUNNING` while any child is still in the `RUNNING` state, and will respond with `FAILURE` upon the first failed child.

Note that "in parallel" here does not mean truly asynchronous execution - children are still ticked first-to-last, so priority order applies if children provide immediate `SUCCESS`/`FAILURE` responses (depending on the chosen `SuccessPolicy`).

### Decorator Nodes

Decorator nodes are branch nodes with a single child that modify the status of their child in some way.

#### Inverse

Inverse nodes flips the result of their child - a `SUCCESS` status is returned as `FAILURE` and vice versa.

#### Blackboard Observer Decorator

BOD nodes watch a blackboard key (for example, the agent's current health) for changes, ticking their child if a given condition evaluates to `true`. Changes to the key trigger an Abort Rule check to dynamically halt execution of child or sibling nodes when met.

#### Request Handler

Request Handler nodes are a subclass of BOD nodes that must have a composite parent. They watch for the observed key and abort any running sibling nodes when it matches a given value.

### Custom Behaviours

Custom behaviours can be defined by extending the `edbt.Behaviour` superclass:

```python

```

## Tree Builder

The library provides a builder-pattern class to assemble behaviour trees in a simple and clear hierarchical structure.

## Development
