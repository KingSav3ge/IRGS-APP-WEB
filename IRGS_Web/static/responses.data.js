// App-owned presentation clauses. No Catalog content or world rules.
const APP_RESPONSE_DATA = {
  "schema_version": 1,
  "id": "irgs-app-routine-v1",
  "version": "1.0.0",
  "language": "en",
  "families": [
    {
      "id": "request.busy",
      "role": "system",
      "state": "busy",
      "source_kind": "host_status",
      "slots": {},
      "fact": "request_status",
      "variants": [
        "Request in progress. You may inspect available records and edit an unsent draft.",
        "Request in progress. Keep any new words as an unsent draft while confirmation arrives.",
        "Request in progress. Available records remain open for inspection."
      ]
    },
    {
      "id": "request.confirmation",
      "role": "system",
      "state": "confirmation",
      "source_kind": "host_status",
      "slots": {},
      "fact": "request_status",
      "variants": [
        "Confirmation is pending. Check the saved request before submitting another attempt.",
        "Confirmation is pending. Look up this request before trying another action.",
        "Confirmation is pending. Your request identity is retained for a saved-result check."
      ]
    },
    {
      "id": "request.pending",
      "role": "system",
      "state": "pending",
      "source_kind": "host_status",
      "slots": {},
      "fact": "request_status",
      "variants": [
        "Your exact declaration is persisted and awaiting resolution. Withdraw it explicitly before revising that pending intent.",
        "Your declaration is saved and awaiting resolution. Withdraw it before replacing that pending intent.",
        "Your exact words are saved as pending intent. Explicit withdrawal is required before changing that declaration."
      ]
    },
    {
      "id": "request.unresolved",
      "role": "system",
      "state": "unresolved",
      "source_kind": "host_status",
      "slots": {},
      "fact": "request_status",
      "variants": [
        "Saved as intent. Freeform declarations cannot be resolved yet. Inspect your records or withdraw this declaration before another action.",
        "Saved as intent. Freeform declarations remain unresolved. Your exact words are retained; inspect or withdraw the pending declaration.",
        "Saved as intent. Freeform declarations have no resolved outcome here. Inspect the record or withdraw the pending declaration."
      ]
    },
    {
      "id": "actor.required",
      "role": "system",
      "state": "required",
      "source_kind": "host_status",
      "slots": {},
      "fact": "actor.required",
      "variants": [
        "A selected player character is required before declaring an action.",
        "Select a player character before declaring an action.",
        "Choose the player character whose intention you want to declare."
      ]
    },
    {
      "id": "actor.unavailable",
      "role": "system",
      "state": "unavailable",
      "source_kind": "host_status",
      "slots": {},
      "fact": "actor.unavailable",
      "variants": [
        "The selected character is not currently available to act. Their identity and history are preserved; no replacement has been selected.",
        "Your selected character is not currently available to act. Their recorded identity and history are retained.",
        "This character is not currently available to act. Their selection remains intact."
      ]
    },
    {
      "id": "request.ready",
      "role": "system",
      "state": "ready",
      "source_kind": "host_status",
      "slots": {},
      "fact": "request_status",
      "variants": [
        "A declaration records your intent. It does not imply an outcome or elapsed time.",
        "Your declaration records an attempt. Its outcome and elapsed time remain unestablished.",
        "Write the intention you want recorded. Declaring it establishes neither success nor elapsed time."
      ]
    },
    {
      "id": "draft.saved",
      "role": "system",
      "state": "saved",
      "source_kind": "host_status",
      "slots": {},
      "fact": "draft.saved",
      "variants": [
        "Unsent draft · saved on this device",
        "Unsent draft · kept on this device",
        "Unsent draft · retained locally"
      ]
    },
    {
      "id": "draft.empty",
      "role": "system",
      "state": "empty",
      "source_kind": "host_status",
      "slots": {},
      "fact": "draft.empty",
      "variants": [
        "Draft stays on this device",
        "Your unsent words stay on this device",
        "Drafts are kept on this device"
      ]
    },
    {
      "id": "draft.copied",
      "role": "system",
      "state": "copied",
      "source_kind": "host_status",
      "slots": {},
      "fact": "draft.copied",
      "variants": [
        "Your words are in the editable response. Nothing has been submitted.",
        "Your words are ready to edit. Nothing has been submitted.",
        "The editable response holds your draft. Nothing has been submitted."
      ]
    },
    {
      "id": "draft.suggested",
      "role": "system",
      "state": "suggested",
      "source_kind": "host_status",
      "slots": {},
      "fact": "draft.suggested",
      "variants": [
        "Suggested response copied to your draft. Edit it or write your own answer, then submit when ready.",
        "The suggested words are now your editable draft. Review them and submit only when ready.",
        "Your draft holds the suggested response. You can edit it or write a different answer before submitting."
      ]
    },
    {
      "id": "review.listed",
      "role": "system",
      "state": "listed",
      "source_kind": "host_status",
      "slots": {},
      "fact": "review.listed",
      "variants": [
        "Nothing is submitted until you confirm. The action may fail when its current requirements are checked.",
        "Review the listed attempt before confirming. Its current requirements are checked on submission, and it may fail.",
        "Confirmation submits this listed attempt. Selecting it alone commits nothing and guarantees no success."
      ]
    },
    {
      "id": "review.edited",
      "role": "system",
      "state": "edited",
      "source_kind": "host_status",
      "slots": {},
      "fact": "review.edited",
      "variants": [
        "Your edited words are an unsent draft. Keep them in your response, or restore the listed wording to confirm this exact action. Different freeform intent remains unresolved.",
        "These edits are an unsent draft. Keep them for editing; different freeform intent remains unresolved.",
        "Your revised words have not been submitted. Keep the draft, or restore the listed wording to confirm that exact action."
      ]
    },
    {
      "id": "review.draft",
      "role": "system",
      "state": "draft",
      "source_kind": "host_status",
      "slots": {},
      "fact": "review.draft",
      "variants": [
        "This is an editable draft starter. Keeping it submits nothing and guarantees no outcome.",
        "Edit these starting words as you wish. Keeping the draft executes no action.",
        "These words suggest an intention. Keep or edit them; nothing is submitted here."
      ]
    },
    {
      "id": "proposal.pending",
      "role": "system",
      "state": "pending",
      "source_kind": "host_status",
      "slots": {},
      "fact": "proposal.pending",
      "variants": [
        "Review requested. Nothing has been executed.",
        "Your proposal review is pending. Nothing has been executed.",
        "Waiting for the requested review. No action has been executed."
      ]
    },
    {
      "id": "proposal.unknown",
      "role": "system",
      "state": "unknown",
      "source_kind": "host_status",
      "slots": {},
      "fact": "proposal.unknown",
      "variants": [
        "The proposal response is uncertain. Check the saved request; this does not start another provider attempt.",
        "The review response is uncertain. Check its saved identity before requesting anything new.",
        "The proposal response is uncertain. A saved-result check makes no new provider attempt."
      ]
    },
    {
      "id": "proposal.ready",
      "role": "system",
      "state": "ready",
      "source_kind": "host_status",
      "slots": {},
      "fact": "proposal.ready",
      "variants": [
        "Proposal ready for your review. Nothing has been executed.",
        "A proposal is ready to review. Acceptance is still yours; nothing has been executed.",
        "Review the proposed action before accepting. Nothing has been executed."
      ]
    },
    {
      "id": "proposal.unavailable",
      "role": "system",
      "state": "unavailable",
      "source_kind": "host_status",
      "slots": {
        "code": "label"
      },
      "fact": "proposal.unavailable",
      "variants": [
        "Assistance unavailable ({code}). Your draft is retained. Cancel this request before trying another.",
        "Assistance unavailable ({code}). Your draft is retained; cancel this request before requesting a fresh review.",
        "Assistance unavailable ({code}). Your draft remains editable. Cancel the old request before another review."
      ]
    },
    {
      "id": "assistance.unconfigured",
      "role": "system",
      "state": "unconfigured",
      "source_kind": "host_status",
      "slots": {},
      "fact": "assistance.unconfigured",
      "variants": [
        "AI assistance is not connected. Listed actions remain available; freeform declarations remain unresolved.",
        "AI assistance is not connected. You can still use listed actions; freeform declarations remain unresolved.",
        "AI assistance is not connected. Existing listed actions are usable and freeform declarations stay unresolved."
      ]
    },
    {
      "id": "assistance.configured",
      "role": "system",
      "state": "configured",
      "source_kind": "host_status",
      "slots": {},
      "fact": "assistance.configured",
      "variants": [
        "Review an assisted proposal for a listed action. Only your explicit acceptance submits it.",
        "You may request an assisted proposal for a listed action. Review it before explicitly accepting.",
        "Assisted review is available for listed actions. Only explicit acceptance submits a proposal."
      ]
    },
    {
      "id": "assistance.unsupported",
      "role": "system",
      "state": "unsupported",
      "source_kind": "host_status",
      "slots": {},
      "fact": "assistance.unsupported",
      "variants": [
        "Assistance is unavailable for this situation. Listed actions remain available; freeform declarations remain unresolved.",
        "This situation has no assisted review available. Listed actions remain usable and freeform declarations remain unresolved.",
        "Assisted review is unavailable here. Use a listed action or keep an unresolved freeform intention."
      ]
    },
    {
      "id": "recovery.uncertain",
      "role": "system",
      "state": "uncertain",
      "source_kind": "host_status",
      "slots": {},
      "fact": "recovery.uncertain",
      "variants": [
        "The request may already be saved. Use Check / retry saved request to retrieve its result before any retry.",
        "The request may already be saved. Check the saved result with the retained identity before retrying.",
        "The request may already be saved. Use Check / retry saved request before considering another submission."
      ]
    },
    {
      "id": "recovery.connection",
      "role": "system",
      "state": "connection",
      "source_kind": "host_status",
      "slots": {},
      "fact": "recovery.connection",
      "variants": [
        "Confirmation pending · request identity retained",
        "Confirmation pending · original identity kept",
        "Confirmation pending · saved-result check available"
      ]
    },
    {
      "id": "request.withdrawn",
      "role": "system",
      "state": "withdrawn",
      "source_kind": "host_status",
      "slots": {},
      "fact": "request_status",
      "variants": [
        "Pending intent withdrawn. The original declaration remains in the record.",
        "Your pending intent was withdrawn. Its original declaration remains recorded.",
        "The unresolved declaration has been withdrawn; its original words remain in the record."
      ]
    },
    {
      "id": "request.recorded",
      "role": "system",
      "state": "recorded",
      "source_kind": "host_status",
      "slots": {},
      "fact": "request_status",
      "variants": [
        "Declaration persisted exactly as submitted. It is awaiting resolution.",
        "Your exact declaration is saved and awaiting resolution.",
        "The submitted words are retained verbatim. Resolution is pending."
      ]
    },
    {
      "id": "request.recorded_unresolved",
      "role": "system",
      "state": "recorded_unresolved",
      "source_kind": "host_status",
      "slots": {},
      "fact": "request_status",
      "variants": [
        "Saved as intent. This build cannot resolve freeform declarations yet. You can inspect your records or withdraw this declaration.",
        "Saved as intent. Freeform declarations remain unresolved; inspect your records or withdraw this declaration.",
        "Saved as intent. Your exact words are retained without a resolved freeform outcome. You can inspect or withdraw the declaration."
      ]
    },
    {
      "id": "result.saved",
      "role": "system",
      "state": "saved",
      "source_kind": "host_status",
      "slots": {},
      "fact": "result.saved",
      "variants": [
        "The committed action result is saved in your record.",
        "Your record contains the committed action result.",
        "The committed result is available in your saved record."
      ]
    },
    {
      "id": "campaign.loading",
      "role": "system",
      "state": "loading",
      "source_kind": "host_status",
      "slots": {},
      "fact": "campaign.loading",
      "variants": [
        "Loading the selected campaign…",
        "Opening the selected campaign…",
        "Reading the selected campaign…"
      ]
    },
    {
      "id": "campaign.restored",
      "role": "system",
      "state": "restored",
      "source_kind": "host_status",
      "slots": {},
      "fact": "campaign.restored",
      "variants": [
        "Campaign restored with its original save.",
        "The original campaign save has been restored.",
        "Your campaign is restored from its retained save."
      ]
    },
    {
      "id": "campaign.trashed",
      "role": "system",
      "state": "trashed",
      "source_kind": "host_status",
      "slots": {},
      "fact": "campaign.trashed",
      "variants": [
        "Campaign moved to Trash. Its complete save can be restored.",
        "The complete campaign save is in Trash and can be restored.",
        "Your campaign is now in Trash. Its complete save remains recoverable."
      ]
    },
    {
      "id": "campaign.branched",
      "role": "system",
      "state": "branched",
      "source_kind": "host_status",
      "slots": {},
      "fact": "campaign.branched",
      "variants": [
        "Independent campaign branch saved.",
        "The independent campaign branch is saved.",
        "Your new campaign branch has been saved."
      ]
    },
    {
      "id": "campaign.changed",
      "role": "system",
      "state": "changed",
      "source_kind": "host_status",
      "slots": {},
      "fact": "campaign.changed",
      "variants": [
        "The visible campaign changed. Select it again before deleting.",
        "The campaign selection changed. Select it again before deletion.",
        "Review the current campaign selection before deleting a campaign."
      ]
    },
    {
      "id": "campaign.created",
      "role": "system",
      "state": "created",
      "source_kind": "host_status",
      "slots": {},
      "fact": "campaign.created",
      "variants": [
        "Campaign started with the character and starting choices you reviewed.",
        "Your campaign has started using the character and choices you reviewed.",
        "The reviewed character and starting choices are saved in your new campaign."
      ]
    },
    {
      "id": "campaign.rise_created",
      "role": "system",
      "state": "rise_created",
      "source_kind": "host_status",
      "slots": {},
      "fact": "campaign.rise_created",
      "variants": [
        "Your founding story is saved. The first choice is yours.",
        "Your founding story has been saved. Choose what to attempt first.",
        "The founding start is saved. Your next decision is yours to make."
      ]
    },
    {
      "id": "campaign.rise_trashed",
      "role": "system",
      "state": "rise_trashed",
      "source_kind": "host_status",
      "slots": {},
      "fact": "campaign.rise_trashed",
      "variants": [
        "Your founding story was already saved and is in Campaign Trash.",
        "The saved founding story is in Campaign Trash.",
        "This founding story already exists in Campaign Trash."
      ]
    },
    {
      "id": "inspection.local",
      "role": "system",
      "state": "local",
      "source_kind": "host_status",
      "slots": {},
      "fact": "inspection.local",
      "variants": [
        "Inspection does not advance the world.",
        "Reading these records advances no world time.",
        "Looking at available records executes no action."
      ]
    },
    {
      "id": "inspection.empty",
      "role": "system",
      "state": "empty",
      "source_kind": "host_status",
      "slots": {},
      "fact": "inspection.empty",
      "variants": [
        "No matching narrative or action records are available. Your confirmed checkpoint remains intact.",
        "No available records match this search. Your saved checkpoint remains intact.",
        "This search found no matching available records. Your campaign checkpoint is unchanged."
      ]
    },
    {
      "id": "usage.loading",
      "role": "system",
      "state": "loading",
      "source_kind": "host_status",
      "slots": {},
      "fact": "usage.loading",
      "variants": [
        "Reading assistance accounting…",
        "Loading saved assistance accounting…",
        "Checking saved usage records…"
      ]
    },
    {
      "id": "usage.unknown",
      "role": "system",
      "state": "unknown",
      "source_kind": "host_status",
      "slots": {},
      "fact": "usage.unknown",
      "variants": [
        "Actual charges remain unknown. Reported tokens are not a verified bill.",
        "Reported tokens describe provider reports; actual charges remain unknown.",
        "Actual charges are unknown. Token reports do not establish a verified bill."
      ]
    },
    {
      "id": "usage.read_only",
      "role": "system",
      "state": "read_only",
      "source_kind": "host_status",
      "slots": {},
      "fact": "usage.read_only",
      "variants": [
        "Refreshing reads saved accounting and never retries this attempt.",
        "Refresh checks saved records without retrying this attempt.",
        "Refreshing the records dispatches no new provider attempt."
      ]
    },
    {
      "id": "ui.unavailable",
      "role": "system",
      "state": "unavailable",
      "source_kind": "host_status",
      "slots": {},
      "fact": "ui.unavailable",
      "variants": [
        "This information is unavailable. Your unsent draft is retained.",
        "The information is unavailable. Your draft remains unsent.",
        "This view has no available information to show. Your draft is retained."
      ]
    },
    {
      "id": "review.proposal",
      "role": "system",
      "state": "proposal",
      "source_kind": "host_status",
      "slots": {
        "action_id": "label"
      },
      "fact": "review.proposal",
      "variants": [
        "The proposal selects {action_id}. Compare this action with your intention. Confirming executes the selected action; provider interpretation can be wrong.",
        "Review {action_id} against your exact intention. Confirming executes that selected action; an interpretation may be wrong.",
        "The selected proposal is {action_id}. Accept only if it expresses your intention; interpretation is not guaranteed."
      ]
    },
    {
      "id": "review.proposal_edited",
      "role": "system",
      "state": "proposal_edited",
      "source_kind": "host_status",
      "slots": {},
      "fact": "review.proposal_edited",
      "variants": [
        "Editing invalidates this proposal. Keep these words as a draft and request a new review.",
        "These edits invalidate the proposal. Keep the changed words as a draft before requesting another review.",
        "The edited intention needs a new review. Keep it as a draft; the old proposal is invalid."
      ]
    },
    {
      "id": "request.rejected",
      "role": "system",
      "state": "rejected",
      "source_kind": "host_status",
      "slots": {
        "reason": "text"
      },
      "fact": "request.rejected",
      "variants": [
        "{reason} Your draft is retained.",
        "{reason} Your unsent draft is retained.",
        "{reason} Your draft remains editable."
      ]
    },
    {
      "id": "receipt.exact",
      "role": "system",
      "state": "committed",
      "source_kind": "committed_receipt",
      "slots": {
        "receipt_text": "text"
      },
      "fact": "receipt",
      "variants": [
        "{receipt_text}"
      ]
    },
    {
      "id": "elapsed.action",
      "role": "system",
      "state": "committed",
      "source_kind": "committed_receipt",
      "slots": {
        "elapsed_seconds": "integer"
      },
      "fact": "action_elapsed",
      "variants": [
        "This action recorded {elapsed_seconds} elapsed seconds.",
        "The recorded duration for this action is {elapsed_seconds} seconds.",
        "This action has a recorded elapsed span of {elapsed_seconds} seconds."
      ]
    },
    {
      "id": "decision.next",
      "role": "system",
      "state": "committed",
      "source_kind": "committed_receipt",
      "slots": {},
      "fact": "next_decision",
      "variants": [
        "Your next choice remains yours.",
        "Review your available choices when ready.",
        "Choose your next intention when you are ready."
      ]
    },
    {
      "id": "player.ask",
      "role": "draft",
      "state": "draft",
      "source_kind": "player_request",
      "slots": {},
      "fact": "intention",
      "variants": [
        "I ask what is expected of me.",
        "I ask for clarification before deciding.",
        "I ask what the request means.",
        "I ask for more detail before I commit to an answer."
      ],
      "title": "Ask for clarification"
    },
    {
      "id": "player.options",
      "role": "draft",
      "state": "draft",
      "source_kind": "player_request",
      "slots": {},
      "fact": "intention",
      "variants": [
        "I ask which options are available to me.",
        "I ask what choices I may consider.",
        "I ask about possible ways forward.",
        "I ask what alternatives I could explore."
      ],
      "title": "Ask about options"
    },
    {
      "id": "player.observe",
      "role": "draft",
      "state": "draft",
      "source_kind": "player_request",
      "slots": {},
      "fact": "intention",
      "variants": [
        "I try to look around carefully.",
        "I take a moment to observe my surroundings.",
        "I try to notice what is visible around me.",
        "I attempt to look more closely before deciding."
      ],
      "title": "Look around"
    },
    {
      "id": "player.explain",
      "role": "draft",
      "state": "draft",
      "source_kind": "player_request",
      "slots": {},
      "fact": "intention",
      "variants": [
        "I explain what I am trying to do.",
        "I state my intention and ask to be heard.",
        "I try to make my intentions clear.",
        "I explain my approach before attempting it."
      ],
      "title": "Explain your intention"
    },
    {
      "id": "player.help",
      "role": "draft",
      "state": "draft",
      "source_kind": "player_request",
      "slots": {},
      "fact": "intention",
      "variants": [
        "I ask whether help is available.",
        "I ask if someone is willing to help.",
        "I try to find out where I could ask for help.",
        "I ask what assistance I might request."
      ],
      "title": "Ask for help"
    },
    {
      "id": "player.prepare",
      "role": "draft",
      "state": "draft",
      "source_kind": "player_request",
      "slots": {},
      "fact": "intention",
      "variants": [
        "I consider what preparation this attempt may need.",
        "I try to work out what I should prepare first.",
        "I ask what preparation would be appropriate.",
        "I consider whether I need to prepare before attempting this."
      ],
      "title": "Consider preparation"
    },
    {
      "id": "player.pause",
      "role": "draft",
      "state": "draft",
      "source_kind": "player_request",
      "slots": {},
      "fact": "intention",
      "variants": [
        "I pause to consider my next choice.",
        "I take a moment to think before deciding.",
        "I hold off while I consider my response.",
        "I try to think through the choice before committing."
      ],
      "title": "Take time to consider"
    },
    {
      "id": "player.decline",
      "role": "draft",
      "state": "draft",
      "source_kind": "player_request",
      "slots": {},
      "fact": "intention",
      "variants": [
        "I decline for now.",
        "I say that I am not ready to agree.",
        "I explain that I do not wish to commit to this yet.",
        "I ask to leave this decision open for now."
      ],
      "title": "Decline for now"
    }
  ],
  "recipes": [
    {
      "id": "result.exact",
      "required": [
        "receipt.exact"
      ],
      "optional": []
    },
    {
      "id": "result.elapsed",
      "required": [
        "receipt.exact",
        "elapsed.action"
      ],
      "optional": [
        "decision.next"
      ]
    },
    {
      "id": "result.next",
      "required": [
        "receipt.exact",
        "decision.next"
      ],
      "optional": [
        "elapsed.action"
      ]
    },
    {
      "id": "request.rejected",
      "required": [
        "request.rejected"
      ],
      "optional": [
        "inspection.local"
      ]
    },
    {
      "id": "recovery.uncertain",
      "required": [
        "recovery.uncertain"
      ],
      "optional": [
        "inspection.local"
      ]
    },
    {
      "id": "review.local",
      "required": [
        "review.listed"
      ],
      "optional": [
        "inspection.local"
      ]
    },
    {
      "id": "draft.kept",
      "required": [
        "draft.copied"
      ],
      "optional": [
        "inspection.local"
      ]
    },
    {
      "id": "usage.local",
      "required": [
        "usage.unknown",
        "usage.read_only"
      ],
      "optional": []
    }
  ]
};
