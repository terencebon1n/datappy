from sqlalchemy import and_, select
from sqlalchemy.orm import aliased

from backend.infrastructure.database.postgres.models.stop import StopModel
from backend.infrastructure.database.postgres.models.stop_time import StopTimeModel
from backend.infrastructure.database.postgres.models.trip import TripModel
from backend.infrastructure.database.repository import AsyncQueryRepository


class TripRepository(AsyncQueryRepository[TripModel]):
    model = TripModel

    async def get_direction(
        self,
        route_id: str,
        origin_name: str,
        destination_name: str,
    ) -> dict:
        st_origin = aliased(StopTimeModel, name="st_origin")
        st_destination = aliased(StopTimeModel, name="st_destination")
        s_origin = aliased(StopModel, name="s_origin")
        s_destination = aliased(StopModel, name="s_destination")

        query = (
            select(
                self.model.direction_id,
                s_origin.id.label("origin_stop_id"),
                s_destination.id.label("destination_stop_id"),
            )
            .select_from(self.model)
            .join(st_destination, st_destination.trip_id == self.model.id)
            .join(s_destination, s_destination.id == st_destination.stop_id)
            .join(st_origin, st_origin.trip_id == self.model.id)
            .join(s_origin, s_origin.id == st_origin.stop_id)
            .where(
                and_(
                    self.model.route_id == route_id,
                    s_destination.name == destination_name,
                    s_origin.name == origin_name,
                    st_destination.stop_sequence > st_origin.stop_sequence,
                )
            )
            .limit(1)
        )

        results = await self.execute_select(query)

        output = results.all()

        if len(output) == 0:
            raise Exception("No direction found")

        return {
            "direction_id": output[0].direction_id,
            "stop_id__origin": output[0].origin_stop_id,
            "stop_id__destination": output[0].destination_stop_id,
        }
