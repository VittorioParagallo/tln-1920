# Mapping di Frame in WN Synsets

Given a set of frames id, get the frame from FrameNet and assign a WordNet Synset to each element.

### Input
The imput is the frameset ids retrieved from the function getFrameSetForStudent() available in notebooks folder.
In this case with the surname 'Paragallo' or 'paragallo' some frames were not feasible so, the dataset was determined by the parameter 'PARAGALLO':

    getFrameSetForStudent('PARAGALLO')
    student: PARAGALLO
    ID: 1071	frame: People_by_vocation  (vocation)
    ID: 1083	frame: Subjective_influence (influence)
    ID: 1017	frame: Noise_makers (makers) attenzione esiste noisemakers
    ID: 2625	frame: Relational_location (location)
    ID:  731	frame: Becoming_silent (silent)

Then one more step has been done to generate an input file with annotated elements. 
The above framesets counts a total of 194 elements between Frame Elements and Lexical units. 

All of these have been manually annotated as requested and recorded in the input file gold.txt:
| FrameId | type | name               | sense       |
|---------|------|--------------------|-------------|
| 1071    | name | People_by_vocation | career.n.01 |
| 1071    | FE   | Origin             | origin.n.02 |
| 1071    | FE   | Person             | person.n.01 |

### Output
The script outputs in a single file 'results.csv' a table with the wordnetsynset for eache element of the frame in the frame set:
Ex:

| FrameId | type | name | sense | gold | score |
|-|-|-|-|-|-|
| 1071 | name | People_by_vocation | career.n.01 | career.n.01 | 1 |
| 1071 | FE | Origin | beginning.n.04 | origin.n.02 | 0 |

## Structure
The scrips is exercise2.py archived in the src and includes:
- main in which all the calls are done
- preprocess to remove punctuation/stopwords/etc
- get_main_clause to split the text in case the multiword is not available in wordnet
- get_wn_ctx to get the context of a word from wordnet as described in the exercise instructions
- bag_of_words to get the similarity score

## Results
The results are in the output folder and are also reported here below for ease of reading.
The overall score is 142/194 (73.20%)	

| FrameId                    | type | name                      | sense                    | gold                   | score |
|----------------------------|------|---------------------------|--------------------------|------------------------|-------|
| 1071                       | name | People_by_vocation        | career.n.01              | career.n.01            | 1     |
| 1071                       | FE   | Origin                    | beginning.n.04           | origin.n.02            | 0     |
| 1071                       | FE   | Person                    | person.n.01              | person.n.01            | 1     |
| 1071                       | FE   | Persistent_characteristic | characteristic.n.02      | characteristic.n.02    | 1     |
| 1071                       | FE   | Descriptor                | form.n.01                | condition.n.01         | 0     |
| 1071                       | FE   | Age                       | age.n.01                 | age.n.01               | 1     |
| 1071                       | FE   | Ethnicity                 | ethnicity.n.01           | ethnicity.n.01         | 1     |
| 1071                       | FE   | Context_of_acquaintance   | acquaintance.n.03        | acquaintance.n.01      | 0     |
| 1071                       | FE   | Rank                      | rank.n.02                | social_station.n.01    | 0     |
| 1071                       | FE   | Place_of_employment       | employment.n.03          | workplace.n.01         | 0     |
| 1071                       | FE   | Employer                  | employer.n.01            | employer.n.01          | 1     |
| 1071                       | FE   | Type                      | character.n.05           | character.n.05         | 1     |
| 1071                       | FE   | Compensation              | compensation.n.01        | recompense.n.02        | 0     |
| 1071                       | FE   | Contract_basis            | footing.n.02             | article.n.03           | 0     |
| 1071                       | LU   | politician.n              | politician.n.02          | politician.n.02        | 1     |
| 1071                       | LU   | farmer.n                  | farmer.n.01              | farmer.n.01            | 1     |
| 1071                       | LU   | attendant.n               | attendant.n.01           | attendant.n.01         | 1     |
| 1071                       | LU   | clerk.n                   | clerk.n.01               | clerk.n.01             | 1     |
| 1071                       | LU   | consultant.n              | adviser.n.01             | adviser.n.01           | 1     |
| 1071                       | LU   | gardener.n                | gardener.n.01            | gardener.n.01          | 1     |
| 1071                       | LU   | lawyer.n                  | lawyer.n.01              | lawyer.n.01            | 1     |
| 1071                       | LU   | maid.n                    | maid.n.01                | maid.n.01              | 1     |
| 1071                       | LU   | manager.n                 | director.n.01            | director.n.01          | 1     |
| 1071                       | LU   | professor.n               | professor.n.01           | professor.n.01         | 1     |
| 1071                       | LU   | receptionist.n            | receptionist.n.01        | receptionist.n.01      | 1     |
| 1071                       | LU   | salesman.n                | salesman.n.01            | salesman.n.01          | 1     |
| 1071                       | LU   | servant.n                 | servant.n.01             | servant.n.01           | 1     |
| 1071                       | LU   | waiter.n                  | waiter.n.01              | waiter.n.01            | 1     |
| 1071                       | LU   | carpenter.n               | carpenter.n.01           | carpenter.n.01         | 1     |
| 1071                       | LU   | scientist.n               | scientist.n.01           | scientist.n.01         | 1     |
| 1071                       | LU   | private_eye.n             | private_detective.n.01   | private_detective.n.01 | 1     |
| 1071                       | LU   | actress.n                 | actress.n.01             | actress.n.01           | 1     |
| 1071                       | LU   | waitress.n                | waitress.n.01            | waitress.n.01          | 1     |
| 1071                       | LU   | technician.n              | technician.n.01          | technician.n.01        | 1     |
| 1071                       | LU   | toxicologist.n            | toxicologist.n.01        | toxicologist.n.01      | 1     |
| 1071                       | LU   | engineer.n                | engineer.n.01            | engineer.n.01          | 1     |
| 1071                       | LU   | double_agent.n            | double_agent.n.01        | double_agent.n.01      | 1     |
| 1071                       | LU   | researcher.n              | research_worker.n.01     | research_worker.n.01   | 1     |
| 1071                       | LU   | archaeologist.n           | archeologist.n.01        | archeologist.n.01      | 1     |
| 1071                       | LU   | professional.a            | professional.a.02        | professional.a.02      | 1     |
| 1071                       | LU   | agent.n                   | agent.n.02               | agent.n.02             | 1     |
| 1071                       | LU   | journalist.n              | journalist.n.01          | journalist.n.01        | 1     |
| 1071                       | LU   | judge.n                   | judge.n.01               | judge.n.01             | 1     |
| 1071                       | LU   | mechanic.n                | automobile_mechanic.n.01 | machinist.n.01         | 0     |
| 1071                       | LU   | oilman.n                  | oilman.n.02              | oilman.n.01            | 0     |
| 1071                       | LU   | reporter.n                | reporter.n.01            | reporter.n.01          | 1     |
| 1071                       | LU   | scholar.n                 | scholar.n.01             | scholar.n.01           | 1     |
| 1071                       | LU   | veterinarian.n            | veterinarian.n.01        | veterinarian.n.01      | 1     |
| 1071                       | LU   | trader.n                  | trader.n.01              | trader.n.01            | 1     |
| 1071                       | LU   | mole.n                    | counterspy.n.01          | counterspy.n.01        | 1     |
| 1071                       | LU   | spy.n                     | spy.n.01                 | spy.n.01               | 1     |
| 1071                       | LU   | businessperson.n          | businessperson.n.01      | businessperson.n.01    | 1     |
| 1071                       | LU   | speculator.n              | speculator.n.02          | speculator.n.02        | 1     |
| 1071                       | LU   | architect.n               | architect.n.01           | architect.n.01         | 1     |
| 1071                       | LU   | plain-clothes_man.n       | serviceman.n.01          | officer.n.04'          | 0     |
| 1071                       | LU   | magistrate.n              | magistrate.n.01          | magistrate.n.01        | 1     |
| 1071                       | LU   | officer.n                 | military_officer.n.01    | officer.n.04           | 0     |
| 1071                       | LU   | police_officer.n          | policeman.n.01           | policeman.n.01         | 1     |
| 1071                       | LU   | spokesperson.n            | spokesperson.n.01        | spokesperson.n.01      | 1     |
| 1071                       | LU   | spokesman.n               | spokesman.n.01           | spokesman.n.01         | 1     |
| 1071                       | LU   | spokeswoman.n             | spokeswoman.n.01         | spokeswoman.n.01       | 1     |
| 1071                       | LU   | policeman.n               | policeman.n.01           | policeman.n.01         | 1     |
| 1071                       | LU   | bodyguard.n               | bodyguard.n.01           | bodyguard.n.01         | 1     |
| 1071                       | LU   | police.n                  | police.n.01              | police.n.01            | 1     |
| 1071                       | LU   | tailor.n                  | tailor.n.01              | tailor.n.01            | 1     |
| 1071                       | LU   | correspondent.n           | correspondent.n.02       | correspondent.n.02     | 1     |
| 1071                       | LU   | cook.n                    | cook.n.01                | cook.n.01              | 1     |
| 1071                       | LU   | manservant.n              | manservant.n.01          | manservant.n.01        | 1     |
| 1071                       | LU   | senator.n                 | senator.n.01             | senator.n.01           | 1     |
| 1071                       | LU   | attorney.n                | lawyer.n.01              | lawyer.n.01            | 1     |
| 1071                       | LU   | athlete.n                 | athlete.n.01             | athlete.n.01           | 1     |
| 1071                       | LU   | chef.n                    | chef.n.01                | chef.n.01              | 1     |
| 1071                       | LU   | bartender.n               | bartender.n.01           | bartender.n.01         | 1     |
| 1071                       | LU   | teacher.n                 | teacher.n.01             | teacher.n.01           | 1     |
| 1071                       | LU   | pilot.n                   | pilot.n.01               | pilot.n.01             | 1     |
| 1071                       | LU   | flight_attendant.n        | steward.n.03             | steward.n.03           | 1     |
| 1071                       | LU   | server.n                  | waiter.n.01              | waiter.n.01            | 1     |
| 1071                       | LU   | software_developer.n      | developer.n.01           | programmer.n.01        | 0     |
| 1071                       | LU   | web_developer.n           | developer.n.01           | programmer.n.01        | 0     |
| 1071                       | LU   | saleswoman.n              | salesgirl.n.01           | salesgirl.n.01         | 1     |
| 1071                       | LU   | salesperson.n             | salesperson.n.01         | salesperson.n.01       | 1     |
| 1071                       | LU   | homemaker.n               | housewife.n.01           | housewife.n.01         | 1     |
| 1071                       | LU   | student.n                 | student.n.01             | student.n.01           | 1     |
| 1071                       | LU   | artist.n                  | artist.n.01              | artist.n.01            | 1     |
| 1071                       | LU   | musician.n                | musician.n.01            | musician.n.01          | 1     |
| 1071                       | LU   | singer.n                  | singer.n.01              | singer.n.01            | 1     |
| 1071                       | LU   | painter.n                 | painter.n.01             | painter.n.01           | 1     |
| 1071                       | LU   | dancer.n                  | dancer.n.01              | dancer.n.01            | 1     |
| 1071                       | LU   | writer.n                  | writer.n.01              | writer.n.01            | 1     |
| 1071                       | LU   | editor.n                  | editor.n.01              | editor.n.01            | 1     |
| 1071                       | LU   | actor.n                   | actor.n.01               | actor.n.01             | 1     |
| 1071                       | LU   | producer.n                | producer.n.02            | producer.n.02          | 1     |
| 1071                       | LU   | director.n                | director.n.03            | director.n.03          | 1     |
| 1071                       | LU   | designer.n                | designer.n.04            | draftsman.n.01         | 0     |
| 1071                       | LU   | neuroscientist.n          | neuroscientist.n.01      | neuroscientist.n.01    | 1     |
| 1071                       | LU   | biologist.n               | biologist.n.01           | biologist.n.01         | 1     |
| 1071                       | LU   | chemist.n                 | chemist.n.01             | chemist.n.01           | 1     |
| 1071                       | LU   | physicist.n               | physicist.n.01           | physicist.n.01         | 1     |
| 1071                       | LU   | anthropologist.n          | anthropologist.n.01      | anthropologist.n.01    | 1     |
| 1071                       | LU   | linguist.n                | linguist.n.01            | linguist.n.01          | 1     |
| 1071                       | LU   | psychologist.n            | psychologist.n.01        | psychologist.n.01      | 1     |
| 1071                       | LU   | psychiatrist.n            | psychiatrist.n.01        | psychiatrist.n.01      | 1     |
| 1071                       | LU   | mathematician.n           | mathematician.n.01       | mathematician.n.01     | 1     |
| 1071                       | LU   | sociologist.n             | sociologist.n.01         | sociologist.n.01       | 1     |
| 1071                       | LU   | fire_fighter.n            | fireman.n.04             | fireman.n.04           | 1     |
| 1071                       | LU   | firefighter.n             | fireman.n.04             | fireman.n.04           | 1     |
| 1071                       | LU   | programmer.n              | programmer.n.01          | programmer.n.01        | 1     |
| 1071                       | LU   | driver.n                  | driver.n.01              | driver.n.01            | 1     |
| 1083                       | name | Subjective_influence      | influence.n.04           | influence.n.04         | 1     |
| 1083                       | FE   | Cognizer                  | None                     | perceiver.n.01         | 0     |
| 1083                       | FE   | Situation                 | situation.n.01           | situation.n.01         | 1     |
| 1083                       | FE   | Entity                    | entity.n.01              | agent.n.01             | 0     |
| 1083                       | FE   | Action                    | natural_process.n.01     | reaction.n.04          | 0     |
| 1083                       | FE   | Behavior                  | behavior.n.04            | behavior.n.02          | 0     |
| 1083                       | FE   | Product                   | product.n.02             | product.n.02           | 1     |
| 1083                       | FE   | Time                      | time.n.01                | time.n.01              | 1     |
| 1083                       | FE   | Event_description         | description.n.01         | situation.n.01         | 0     |
| 1083                       | FE   | Agent                     | agent.n.02               | situation.n.01         | 0     |
| 1083                       | FE   | Place                     | topographic_point.n.01   | place.n.06             | 0     |
| 1083                       | FE   | Domain                    | sphere.n.01              | domain.n.02            | 0     |
| 1083                       | FE   | Descriptor                | form.n.01                | form.n.01              | 1     |
| 1083                       | LU   | impact.v                  | affect.v.01              | affect.v.01            | 1     |
| 1083                       | LU   | influential.a             | influential.a.01         | influential.a.01       | 1     |
| 1083                       | LU   | inspire.v                 | cheer.v.05               | inspire.v.02           | 0     |
| 1083                       | LU   | influence.v               | influence.v.01           | influence.v.01         | 1     |
| 1083                       | LU   | influence.n               | influence.n.03           | influence.n.04         | 0     |
| 1083                       | LU   | inspiration.n             | inspiration.n.01         | inspiration.n.01       | 1     |
| 1083                       | LU   | effect.n                  | consequence.n.01         | consequence.n.01       | 1     |
| 1083                       | LU   | impact.n                  | impact.n.02              | impact.n.02            | 1     |
| 1083                       | LU   | drive.v                   | drive.v.07               | drive.v.07             | 1     |
| 1083                       | LU   | motivate.v                | motivate.v.01            | motivate.v.01          | 1     |
| 1083                       | LU   | push.v                    | push.v.01                | push.v.02              | 0     |
| 1083                       | LU   | galvanize.v               | startle.v.01             | startle.v.01           | 1     |
| 1083                       | LU   | coax.v                    | wheedle.v.01             | wheedle.v.01           | 1     |
| 1083                       | LU   | entice.v                  | entice.v.01              | entice.v.01            | 1     |
| 1083                       | LU   | spur.v                    | spur.v.01                | spur.v.01              | 1     |
| 1083                       | LU   | tempt.v                   | tempt.v.01               | entice.v.01            | 0     |
| 1083                       | LU   | discourage.v              | discourage.v.02          | discourage.v.02        | 1     |
| 1083                       | LU   | encourage.v               | encourage.v.02           | encourage.v.02         | 1     |
| 1083                       | LU   | goad.v                    | spur.v.02                | goad.v.02              | 0     |
| 1083                       | LU   | stimulate.v               | stimulate.v.01           | stimulate.v.03         | 0     |
| 1017                       | name | Noise_makers              | noisemaker.n.01          | noisemaker.n.01        | 1     |
| 1017                       | FE   | Noise_maker               | noisemaker.n.01          | noisemaker.n.01        | 1     |
| 1017                       | FE   | Use                       | manipulation.n.01        | function.n.02          | 0     |
| 1017                       | FE   | Creator                   | creator.n.02             | creator.n.02           | 1     |
| 1017                       | FE   | Time_of_creation          | creation.n.02            | time.n.05              | 0     |
| 1017                       | FE   | Name                      | name.v.01                | name.n.01              | 0     |
| 1017                       | FE   | Type                      | type.n.01                | type.n.01              | 1     |
| 1017                       | FE   | Material                  | material.n.01            | material.n.01          | 1     |
| 1017                       | FE   | Ground                    | ground.v.03              | location.n.01          | 0     |
| 1017                       | LU   | guitar.n                  | guitar.n.01              | guitar.n.01            | 1     |
| 1017                       | LU   | bell.n                    | bell.n.01                | bell.n.01              | 1     |
| 1017                       | LU   | siren.n                   | siren.n.04               | siren.n.04             | 1     |
| 1017                       | LU   | piano.n                   | piano.n.01               | piano.n.01             | 1     |
| 1017                       | LU   | rattle.n                  | rattle.n.02              | rattle.n.02            | 1     |
| 1017                       | LU   | xylophone.n               | marimba.n.01             | marimba.n.01           | 1     |
| 1017                       | LU   | drum.n                    | drum.n.01                | drum.n.01              | 1     |
| 1017                       | LU   | cello.n                   | cello.n.01               | cello.n.01             | 1     |
| 1017                       | LU   | saxophone.n               | sax.n.02                 | sax.n.02               | 1     |
| 1017                       | LU   | alarm.n                   | alarm.n.02               | alarm.n.02             | 1     |
| 2625                       | name | Relational_location       | location.n.01            | location.n.01          | 1     |
| 2625                       | FE   | Profiled_region           | region.n.01              | region.n.01            | 1     |
| 2625                       | FE   | Constituent_parts         | part.n.01                | parts.n.01             | 0     |
| 2625                       | FE   | Relative_location         | location.n.01            | localization.n.01      | 0     |
| 2625                       | FE   | Formational_cause         | cause.n.02               | causal_agent.n.01      | 0     |
| 2625                       | FE   | Container_possessor       | owner.n.02               | owner.n.02             | 1     |
| 2625                       | FE   | Descriptor                | form.n.01                | descriptor.n.02        | 0     |
| 2625                       | FE   | Related_event             | consequence.n.01         | event.n.02             | 0     |
| 2625                       | FE   | Inherent_purpose          | determination.n.02       | purpose.n.01           | 0     |
| 2625                       | FE   | Ground                    | land.n.04                | location.n.01          | 0     |
| 731                        | name | Becoming_silent           | silent.s.04              | quieten.v.01           | 0     |
| 731                        | FE   | Speaker                   | speaker.n.01             | speaker.n.01           | 1     |
| 731                        | FE   | Topic                     | subject.n.01             | subject.n.01           | 1     |
| 731                        | FE   | Place                     | topographic_point.n.01   | topographic_point.n.01 | 1     |
| 731                        | FE   | Time                      | time.v.05                | time.n.01              | 0     |
| 731                        | FE   | Expressor                 | None                     | speaker.n.03           | 0     |
| 731                        | FE   | Manner                    | manner.n.01              | manner.n.01            | 1     |
| 731                        | FE   | Explanation               | explanation.n.01         | explanation.n.01       | 1     |
| 731                        | LU   | button_(one's)_lip.v      | None                     | shush.v.01             | 0     |
| 731                        | LU   | hold_(one's)_tongue.idio  | natural_language.n.01    | shush.v.01             | 0     |
| 731                        | LU   | hush.v                    | hush.v.01                | hush.v.01              | 1     |
| 731                        | LU   | hush_up.v                 | whitewash.v.01           | hush.v.02              | 0     |
| 731                        | LU   | quiet.v                   | calm.v.01                | quieten.v.01           | 0     |
| 731                        | LU   | quiet_down.v              | quieten.v.01             | quieten.v.01           | 1     |
| 731                        | LU   | shush.v                   | shush.v.01               | shush.v.01             | 1     |
| 731                        | LU   | shut_up.v                 | close_up.v.04            | close_up.v.04          | 1     |
| 731                        | LU   | stow_it.v                 | stow.v.01                | quieten.v.01           | 0     |
| 731                        | LU   | silence.v                 | hush.v.02                | silence.v.02           | 0     |
| 731                        | LU   | sh.intj                   | None                     | shush.v.01             | 0     |
| 731                        | LU   | quieten.v                 | quieten.v.01             | quieten.v.01           | 1     |
| 731                        | LU   | pipe_down.v               | quieten.v.01             | quieten.v.01           | 1     |
| 731                        | LU   | quiet.n                   | tranquillity.n.01        | silence.n.02           | 0     |
| 731                        | LU   | seal_(one's)_lips.v       | None                     | shush.v.01             | 0     |
| 731                        | LU   | not_a_word.idio           | word.n.01                | shush.v.01             | 0     |
| ACCURACY: 142/194 (73.20%) |      |                           |                          |                        |       |

## Authors

- Vittorio Paragallo