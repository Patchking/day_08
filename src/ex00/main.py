#-----------------#
# Task code start #
#-----------------#

import asyncio

from enum import Enum, auto
from random import choice

class Action(Enum):
    HIGHKICK = auto()
    LOWKICK = auto()
    HIGHBLOCK = auto()
    LOWBLOCK = auto()


class Agent:

    def __aiter__(self, health=5):
        self.health = health
        self.actions = list(Action)
        return self

    async def __anext__(self):
        return choice(self.actions)

#---------------#
# Task code end #
#---------------#

import random, time

MINMAX_DELEY = (0.5, 1.0)

async def curent_aciton_corutine(ag: Agent, agent_number, action):
    await asyncio.sleep(random.uniform(*MINMAX_DELEY))
    if action == Action.HIGHKICK:
        neo_action = Action.HIGHBLOCK
    elif action == Action.LOWKICK:
        neo_action = Action.LOWBLOCK
    elif action == Action.HIGHBLOCK:
        neo_action = Action.LOWKICK
        ag.health -= 1
    elif action == Action.LOWBLOCK:
        neo_action = Action.HIGHKICK
        ag.health -= 1
    print(f"Agent {agent_number}: {action}, Neo: {neo_action}, Agent Health: {ag.health}")
    if ag.health == 0:
        raise Exception("Agent died")

async def fight(ag: Agent, ag_num):
    try:
        async with asyncio.TaskGroup() as tg:
            async for action in ag:
                await asyncio.sleep(0.1)
                tg.create_task(curent_aciton_corutine(ag, ag_num, action))
    except Exception:
        return
    
async def fightmany(aglist: list):
    async with asyncio.TaskGroup() as tg:
        for i, ag in enumerate(aglist):
            tg.create_task(fight(ag, i))
    print("Neo wins!")

if __name__ == '__main__':
    #fight
    starttime = time.time()
    asyncio.run(fight(Agent(), 1))
    endtime = time.time()
    print("Time to complete fight()", endtime - starttime)

    #fightmany
    agents = [Agent() for _ in range(3)]
    starttime = time.time()
    asyncio.run(fightmany(agents))
    endtime = time.time()
    print("Time to complete fightmany()", endtime - starttime)
