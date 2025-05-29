class Entity:

    def __init__(self, entity_id):
        self.id = entity_id
        self.components = {}

    def add_component(self, component_type, component):
        self.components[component_type] = component

    def get_component(self, component_type):
        return self.components.get(component_type)


class PositionComponent:

    def __init__(self, x, y):
        self.x = x
        self.y = y


class VelocityComponent:

    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy


class World:

    def __init__(self):
        self.entities = []
        self.systems = []

    def create_entity(self):
        entity = Entity(len(self.entities))
        self.entities.append(entity)
        return entity

    def add_system(self, system):
        self.systems.append(system)

    def update(self):
        for system in self.systems:
            for entity in self.entities:
                for component_type in entity.components:
                    if system.can_process(entity, component_type):
                        system.process(entity)


class MovementSystem:

    def can_process(self, entity, component_type):
        return entity.get_component(PositionComponent
            ) and entity.get_component(VelocityComponent)

    def process(self, entity):
        pos = entity.get_component(PositionComponent)
        vel = entity.get_component(VelocityComponent)
        if pos and vel:
            pos.x += vel.dx
            pos.y += vel.dy


def main():
    world = World()
    movement_system = MovementSystem()
    world.add_system(movement_system)
    for i in range(1000):
        entity = world.create_entity()
        entity.add_component(PositionComponent, PositionComponent(i, i))
        entity.add_component(VelocityComponent, VelocityComponent(1, 1))
    for frame in range(60):
        world.update()


if __name__ == '__main__':
    main()
