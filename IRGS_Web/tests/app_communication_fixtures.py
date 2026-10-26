"""Explicit temporary communication selections for tests, never product setup."""
import uuid
from core_world import CoreWorld
from r9_runtime import grant
from settlement_setup import initialize, preview
from test_scene_actions import fixture as scene_fixture, apply
from test_settlement import choices


def introduce(world, listener, speaker, text=None):
    key='introduction:'+listener+':'+speaker
    apply(world,key,'record_evidence',evidence_id=key,subject=listener,originator=speaker,
          assertion=text or 'Received attribution from '+speaker+'. Current presence is not certified.',status='testimony')
    apply(world,key+':received','receive_evidence',evidence_id=key,recipient=listener)


def install(store):
    scene=scene_fixture()
    apply(scene,'communication-witness','register_actor',actor_id='witness',name='UNRECEIVED_WITNESS_NAME',species='human',player_controlled=False)
    apply(scene,'communication-hidden','register_actor',actor_id='hidden',name='PRIVATE_CHANNEL_ROSTER',species='human',player_controlled=False)
    scene.s['actors']['witness']['current']['location']='quay'
    scene.s['actors']['hidden']['current']['location']='PRIVATE_LOCATION'
    introduce(scene,'pc','witness')
    scene.s['communication_rules']={'schema_version':1,'source_ref':'synthetic-reviewed-quay-channel',
        'time_model':'causal_only_no_elapsed_rule','channels':{'quay':{'mode':'co_located','actors':['pc','witness','hidden']}}}
    quay=uuid.uuid4().hex
    store.write({'id':quay,'name':'Selected quay communication fixture','revision':1,'state':scene.s})
    selected=choices();selected['permission']='held'
    rise=initialize(selected,preview(selected)['review_digest'],'synthetic-selected-communication')
    # Explicit solo test ownership of several characters, never an NPC choice.
    rise.s['player_actor_ids']=['founder','oren','elin']
    for actor in ('founder','oren'):
        grant(rise,actor+'-custody',actor,['transfer_stock'],rise.s['clock']+1,'synthetic selected custody')
    rise.s['communication_rules']={'schema_version':1,'source_ref':'synthetic-reviewed-R00-channel',
        'time_model':'causal_only_no_elapsed_rule','stock_profile':'settlement_free_stock',
        'channels':{'local':{'mode':'co_located','actors':['founder','oren','elin']}},
        'stock_authorities':{'founder-custody':['founder-home'],'oren-custody':['oren-home']}}
    introduce(rise,'founder','oren','Oren attribution. Proposal references: founder-home, oren-home, grain, founder-custody. This testimony grants no rights or stock.')
    introduce(rise,'oren','founder','Founder attribution. Proposal references: oren-home, founder-home, grain, oren-custody. This testimony grants no rights or stock.')
    settlement=uuid.uuid4().hex
    store.write({'id':settlement,'name':'Selected R00 communication fixture','revision':1,'state':rise.s})
    return {'quay':quay,'rise':settlement}
