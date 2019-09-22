## rasa extension plugin

Extends rasa core through component plugin to include:

**max_event_history** :  limits the tracker to maximum of latest 'N ' events

**ExtendedDialogueStateTracker**: optimize payload to action server to exclude tracker events.



## Installation

* Install the plugin (requires python3)

  Online from pypi:

  ```shell
  pip install rasa-ext-plugin
  ```

  Offline:

  ```shell
  git clone https://github.com/AppliedSoul/rasa_ext_plugin.git
  pip install -e rasa_ext_plugin
  ```

  

* In RASA **endpoints.yaml** , setup the plugin tracker store

  ```yaml
  ###########################################################
  # limiter tracker for existing store types : 
  # rasa_ext_plugin.core.tracker_store.InMemoryLimiterTrackerStore
  # rasa_ext_plugin.core.tracker_store.RedisLimiterTrackerStore
  # rasa_ext_plugin.core.tracker_store.MongoLimiterTrackerStore
  # rasa_ext_plugin.core.tracker_store.SQLLimiterTrackerStore
  #
  # All limiter tracker store optionally accepts: 
  # max_event_history - limit maximum events tracked by tracker
  ############################################################
  
  #tracker_store:
  #  type: rasa_ext_plugin.core.tracker_store.InMemoryLimiterTrackerStore
  #  url: localhost
  #  max_event_history: 40
    
  tracker_store:
      type: rasa_ext_plugin.core.tracker_store.RedisLimiterTrackerStore
      url: localhost
      port: 6379
      db: 0
  #    password:
  #    record_exp:
      max_event_history: 40
      
  ```

* Startup the rasa server.



## Customizing tracker payload sent to remote action server

Refer to  [tracker_store]  _ExtendedDialogueStateTracker_  , modify the return state from  *current\_state* method.

```python
class ExtendedDialogueStateTracker(DialogueStateTracker):    
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
```


