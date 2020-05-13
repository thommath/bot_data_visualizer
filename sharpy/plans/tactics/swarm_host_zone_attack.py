from enum import Enum
from typing import Optional  # , List

from .zone_attack import AttackStatus, PlanZoneAttack

from sharpy.plans.acts import ActBase
from sharpy.managers.game_states.advantage import (
    at_least_small_disadvantage,
    at_least_small_advantage,
    at_least_clear_advantage,
    at_least_clear_disadvantage,
)
from sharpy.general.zone import Zone
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units
from sc2.ids.unit_typeid import UnitTypeId

from sharpy.managers.roles import UnitTask
from sharpy.knowledges import Knowledge
from sharpy.managers.combat2 import MoveType
from sharpy.general.extended_power import ExtendedPower
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sharpy.managers import *

ENEMY_TOTAL_POWER_MULTIPLIER = 1.2

RETREAT_TIME = 20

RETREAT_STOP_DISTANCE = 5
RETREAT_STOP_DISTANCE_SQUARED = RETREAT_STOP_DISTANCE * RETREAT_STOP_DISTANCE


class SwarmHostZoneAttack(PlanZoneAttack):
    """Modification of PlanZoneAttack to use Locust CD when available."""

    def handle_attack(self, target):
        """Changed to operated around Locust CD if Swarm Hosts are present."""
        already_attacking: Units = self.knowledge.roles.units(UnitTask.Attacking)
        if not already_attacking.exists:
            self.print("No attacking units, starting retreat")
            # All attacking units have been destroyed.
            self._start_retreat(AttackStatus.Retreat)
            return True

        center = already_attacking.center
        front_runner = already_attacking.closest_to(target)

        # target = self.pather.find_path(center, target)

        for unit in already_attacking:
            # Only units in group are included to current combat force
            self.combat.add_unit(unit)

        for unit in self.knowledge.roles.free_units:
            if self.knowledge.should_attack(unit):
                p: Point2 = unit.position

                if not self.knowledge.roles.is_in_role(UnitTask.Attacking, unit) and (
                    unit.distance_to(center) > 20 or unit.distance_to(front_runner) > 20
                ):
                    self.knowledge.roles.set_task(UnitTask.Moving, unit)
                    # Unit should start moving to target position.
                    self.combat.add_unit(unit)
                else:
                    self.knowledge.roles.set_task(UnitTask.Attacking, unit)
                    already_attacking.append(unit)
                    # Unit should start moving to target position.
                    self.combat.add_unit(unit)

        # Execute
        # Check if half SHs have Locusts available
        for self.cache.own(UnitTypeId.SWARMHOSTMP)
        self.combat.execute(target, MoveType.Assault)

        retreat = self._should_retreat(front_runner.position, already_attacking)

        if retreat != AttackStatus.NotActive:
            self._start_retreat(retreat)
