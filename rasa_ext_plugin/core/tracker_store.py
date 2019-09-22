#import logging
from typing import Optional, Text, Union, Dict, Any

from rasa.core.domain import Domain
from rasa.core.trackers import DialogueStateTracker, EventVerbosity

from rasa.core.tracker_store import TrackerStore, InMemoryTrackerStore, RedisTrackerStore, MongoTrackerStore, SQLTrackerStore


##
# 
# Extending Tracker & Stores to include: 
# max_event_history : maximum number of latest events to track 
# by the tracker
# ExtendedDialogueStateTracker: tracker with its state optimized 
# for sending to action server
#
##

#logger = logging.getLogger(__name__)

# Extended tracker manupulates tracker state sent to 
# remote action server. Original tracker state has
# verbose metadata.
class ExtendedDialogueStateTracker(DialogueStateTracker):
    def __init__(self, sender_id, slots, max_event_history=None):
        super(ExtendedDialogueStateTracker, self).__init__(sender_id, slots, max_event_history)
    
    # override 
    # Actions uses this method to collect tracker's metadata
    # before sending payload as json.
    def current_state(
        self, event_verbosity: EventVerbosity = EventVerbosity.NONE
    ) -> Dict[Text, Any]:
        # conversation state format
        #  {
        #    "sender_id": self.sender_id,
        #    "slots": self.current_slot_values(),
        #    "latest_message": self.latest_message.parse_data,
        #    "latest_event_time": latest_event_time,
        #    "followup_action": self.followup_action,
        #    "paused": self.is_paused(),
        #    "events": evts,
        #    "latest_input_channel": self.get_latest_input_channel(),
        #    "active_form": self.active_form,
        #    "latest_action_name": self.latest_action_name,
        # }
        state = super(ExtendedDialogueStateTracker,self).current_state(event_verbosity)
        
        #
        # request payload to action server contains tracker information
        # from this state 

        # removing events from state information
        # action server currently ignores event history
        # reduces size of request payload to action server
        # 
        # additional unwanted keys can be poped to reduce size
        #
        state.pop("events", None)
        
        return state


# Extended tracker store to incoporate 
# max_event_history : maximum number of latest events to track 
# by the tracker
# ExtendedDialogueStateTracker: tracker with its state optimized 
# for sending to action server
class ExtendedTrackerStore(TrackerStore):
    def __init__(self, domain: Domain, event_broker = None, max_event_history: Optional[int] = None) -> None:
        super(ExtendedTrackerStore, self).__init__(domain, event_broker)
        self.max_event_history = max_event_history

    # override
    # include limit when creating tracker
    def get_or_create_tracker(self, sender_id, max_event_history=None):
        return super(ExtendedTrackerStore, self).get_or_create_tracker(sender_id, self.max_event_history)

    # setter for limit, needed to make mixin work
    def set_max_event_history(self, max_event_history: Optional[int] = None):
        self.max_event_history = max_event_history

    # override
    # return extended tracker instead of original
    def init_tracker(self, sender_id):
        return ExtendedDialogueStateTracker(
            sender_id,
            self.domain.slots if self.domain else None,
            max_event_history=self.max_event_history,
        )


#
# Extending original tracker stores to incoporate extended tracker and store 
#

# In Memory tracker store implementation
class InMemoryLimiterTrackerStore(InMemoryTrackerStore, ExtendedTrackerStore):
    def __init__(self, domain: Domain, event_broker = None, url: Optional[str] = None, max_event_history:Optional[int] = None) -> None:
        super(InMemoryLimiterTrackerStore, self).__init__(domain, event_broker)
        self.set_max_event_history(max_event_history)


# Redis Tracker store implementation
class RedisLimiterTrackerStore(RedisTrackerStore, ExtendedTrackerStore):
    def __init__(self, domain: Domain, event_broker = None, url: Optional[str] = None, max_event_history:Optional[int] = None, **kwargs) -> None:
        super(RedisLimiterTrackerStore, self).__init__(domain, event_broker, **kwargs)
        self.set_max_event_history(max_event_history)


# Mongodb Tracker store implementation
class MongoLimitedTrackerStore(MongoTrackerStore, ExtendedTrackerStore):
    def __init__(self, domain: Domain, event_broker = None, url: Optional[str] = None, max_event_history:Optional[int] = None, **kwargs) -> None:
        super(MongoLimitedTrackerStore, self).__init__(domain, event_broker, **kwargs)
        self.set_max_event_history(max_event_history)


#Sql tracker store implementation
class SQLLimiterTrackerStore(SQLTrackerStore, ExtendedTrackerStore):
    def __init__(self, domain: Domain, event_broker = None, url: Optional[str] = None, max_event_history:Optional[int] = None, **kwargs) -> None:
        super(SQLLimiterTrackerStore, self).__init__(domain, event_broker, **kwargs)
        self.set_max_event_history(max_event_history)



