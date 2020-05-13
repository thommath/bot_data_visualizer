import math
import os
import jsonpickle
import matplotlib.pyplot as plt
from sc2 import Race
from sharpy.tools.opponent_data import OpponentData, GameResult

directory = os.fsencode('./data')

results = []

for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".json"): 
        print(filename)

        with open(os.path.join(directory, file), 'r') as jsonFile:
            data: OpponentData = jsonpickle.decode(jsonFile.read())

            for a in data.results:
                a: GameResult = a
                a.enemy_id = data.enemy_id
                results.append(a)

                print(a.enemy_race, getattr(a, 'bot_version',["v0.2.2"])[0])

        continue
    else:
        continue


plt.subplot(2, 2, 1)
plt.plot(
    [time for time in range(0, math.floor(max(a.game_duration for a in results)), 50)],
    [sum(a.result for a in results if a.game_duration < time and a.game_duration > time-50 and a.result == 1) for time in range(0, math.floor(max(a.game_duration for a in results)), 50)],
    [time for time in range(0, math.floor(max(a.game_duration for a in results)), 50)],
    [-sum(a.result for a in results if a.game_duration < time and a.game_duration > time-50 and a.result == -1) for time in range(0, math.floor(max(a.game_duration for a in results)), 50)]
    )
plt.xlabel('Total win, loss over time')


plt.subplot(2, 2, 2)
plt.plot(
    [time for time in range(0, math.floor(max(a.game_duration for a in results)), 50)],
    [sum(a.result for a in results if a.enemy_race == Race.Zerg and a.game_duration < time and a.game_duration > time-50 and a.result == 1) for time in range(0, math.floor(max(a.game_duration for a in results)), 50)],
    [time for time in range(0, math.floor(max(a.game_duration for a in results)), 50)],
    [-sum(a.result for a in results if a.enemy_race == Race.Zerg and a.game_duration < time and a.game_duration > time-50 and a.result == -1) for time in range(0, math.floor(max(a.game_duration for a in results)), 50)]    
)
plt.subplot(2, 2, 3)
plt.plot(
    [time for time in range(0, math.floor(max(a.game_duration for a in results)), 50)],
    [sum(a.result for a in results if a.enemy_race == Race.Protoss and a.game_duration < time and a.game_duration > time-50 and a.result == 1) for time in range(0, math.floor(max(a.game_duration for a in results)), 50)],
    [time for time in range(0, math.floor(max(a.game_duration for a in results)), 50)],
    [-sum(a.result for a in results if a.enemy_race == Race.Protoss and a.game_duration < time and a.game_duration > time-50 and a.result == -1) for time in range(0, math.floor(max(a.game_duration for a in results)), 50)]    
)
plt.subplot(2, 2, 4)
plt.plot(
    [time for time in range(0, math.floor(max(a.game_duration for a in results)), 50)],
    [sum(a.result for a in results if a.enemy_race == Race.Terran and a.game_duration < time and a.game_duration > time-50 and a.result == 1) for time in range(0, math.floor(max(a.game_duration for a in results)), 50)],
    [time for time in range(0, math.floor(max(a.game_duration for a in results)), 50)],
    [-sum(a.result for a in results if a.enemy_race == Race.Terran and a.game_duration < time and a.game_duration > time-50 and a.result == -1) for time in range(0, math.floor(max(a.game_duration for a in results)), 50)]    
)


def autolabel(rects, amounts):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for i in range(len(rects)):
        rect = rects[i]
        amount = amounts[i]
        height = rect.get_height()
        ax.annotate('{}'.format(amount),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

races = [
    Race.Zerg,
    Race.Protoss,
    Race.Terran
]

results_for_races = list(map(lambda race: \
    list(filter(lambda result: result.enemy_race == race, results)), races))

versions = sorted(set(map(lambda result: getattr(result, 'bot_version',["v0.2.2"])[0], results)))

version_filter = lambda ver, results_input: filter(lambda result: getattr(result, 'bot_version',["v0.2.2"])[0] == ver, results_input)

print(versions)


### 
### Plot win rate for races over versions
###
fig, ax = plt.subplots()

n = -0.5
width = 0.7 * 1/len(versions)
for ver in versions:
    rects1 = ax.bar(
        [x + n * width for x in range(0, 3)],
        [len(list(filter(lambda res: res.result == 1, version_filter(ver, race_result)))) / len(list(version_filter(ver, race_result))) if len(list(version_filter(ver, race_result))) != 0 else 0 for race_result in results_for_races],
        width=width,
        label=ver
    )
    n += 1
    autolabel(rects1, [len(list(version_filter(ver, race_result))) for race_result in results_for_races])

ax.set_ylabel('Win percent')
ax.set_title('Win rate by race for versions')
ax.set_xticks([0, 1, 2])
ax.set_xticklabels(["Zerg", "Protoss", "Terran"])
ax.legend()

fig.tight_layout()

###
### Plot win rate against bots over versions
###

fig, ax = plt.subplots()

enemies = set(map(lambda result: result.enemy_id, results))


results_for_bots = list(map(lambda bot: \
    list(filter(lambda result: result.enemy_id == bot, results)), enemies))

def win_rate_for_version(ver, results):
    won_ver = len(list(filter(lambda res: res.result == 1, version_filter(ver, enemy_results))))
    total_ver = len(list(version_filter(ver, enemy_results)))
    return won_ver, last_total_ver

iterable_version = list(iter(versions))

n = -0.5
width = 0.9 * 1/len(versions)

to_plot = []

for i in range(len(versions)):
    ver = iterable_version[i]
    last_ver = iterable_version[i-1] if i != 0 else ""

    height_plot = []

    for enemy_results in results_for_bots:

        won_ver = len(list(filter(lambda res: res.result == 1, version_filter(ver, enemy_results))))
        total_ver = len(list(version_filter(ver, enemy_results)))

        
        if last_ver:
            last_won_ver = len(list(filter(lambda res: res.result == 1, version_filter(last_ver, enemy_results))))
            last_total_ver = len(list(version_filter(last_ver, enemy_results)))

        else:
            last_won_ver = 0
            last_total_ver = 0

        if total_ver == 0:
            height_plot.append(0)
        elif i == 0:
            height_plot.append(0)
        elif last_total_ver == 0:
            found = False
            for o in range(i, 0, -1):
                last_won_ver, last_total_ver = win_rate_for_version(iterable_version[0], enemy_results)
                if last_total_ver != 0:
                    found = True
                    if (won_ver / total_ver) == (last_won_ver / last_total_ver):
                        height_plot.append(0)
                    elif (won_ver / total_ver) > (last_won_ver / last_total_ver):
                        height_plot.append(1)
                    else:
                        height_plot.append(-1)
                    break
            
            if not found:
                height_plot.append((won_ver / total_ver))
        else:
            if (won_ver / total_ver) == (last_won_ver / last_total_ver):
                height_plot.append(0)
            elif (won_ver / total_ver) > (last_won_ver / last_total_ver):
                height_plot.append(1)
            else:
                height_plot.append(-1)
    
    to_plot.append(sum(height_plot))

rects1 = ax.bar(
    [x for x in range(0, len(versions))],
    to_plot
)
#    autolabel(rects1, [len(list(version_filter(ver, race_result))) for race_result in results_for_bots])

ax.set_ylabel('Number of bots win percentage has changed against')
ax.set_title('Win rate increased versus enemies for versions')
ax.set_xticks(list(range(len(versions))))
ax.set_xticklabels([x for x in versions])
ax.legend()

fig.tight_layout()

plt.show()
"""

races_won = [0, 0, 0]
races_lost = [0, 0, 0]
for game in results:
    list_to_use = None
    if game.result == 1:
        list_to_use = races_won
    else:
        list_to_use = races_lost

    if game.enemy_race == Race.Zerg:
        list_to_use[0] += 1
    if game.enemy_race == Race.Protoss:
        list_to_use[1] += 1
    if game.enemy_race == Race.Terran:
        list_to_use[2] += 1

print(races_won, races_lost)

plt.subplot(2, 2, 2)
plt.bar(
    ["Zerg", "Protoss", "Terran"],
    [races_won[i] / (races_won[i] + races_lost[i]) for i in range(0, 3)],
)
"""