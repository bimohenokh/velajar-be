import traceback

from django.utils import timezone
from django_q.models import Schedule

from taschoolassistant.chain_notes.models import ChainNote, ChainNoteTurn


def check_chain_note_finished_name(chain_note_id):
    return f"check_chain_note_finished_id_{chain_note_id}"

# TODO tambahin croniter
def check_chain_note_finished(chain_note_id):
    try:
        chain_note = ChainNote.objects.get(id=chain_note_id)

        if chain_note.is_ended:
            print(f"Chain note {chain_note_id} is already finished.")
            Schedule.objects.filter(name=check_chain_note_finished_name(chain_note_id)).delete()
            return

        available_chain_note_turns = ChainNoteTurn.objects.filter_available_turn_by_chain_note(chain_note)
        if not available_chain_note_turns.exists():
            print(f"Chain note {chain_note_id} has no available turns left.")
            chain_note.status = ChainNote.Status.FINISHED
            chain_note.save()
            Schedule.objects.filter(name=check_chain_note_finished_name(chain_note_id)).delete()
            return

        print(f"Chain note {chain_note_id} is not finished.")

    except ChainNote.DoesNotExist:
        print(f"Chain note {chain_note_id} does not exist.")
        Schedule.objects.filter(name=check_chain_note_finished_name(chain_note_id)).delete()
        return

    except Exception as e:
        error_traceback = traceback.format_exc()
        print(error_traceback)
        return