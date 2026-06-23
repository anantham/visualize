You are compiling a rigorously fact-checked dataset for a history-of-ideas visualization (a globe + timeline showing how schools of thought influenced each other and spread across the world). Do NOT ask me any clarifying questions — make reasonable scholarly assumptions and proceed. Use web research and cite sources. Where scholars disagree on a date, give the mainstream consensus and set uncertain: true.

# Your task

For EACH of the thinkers listed in the ROSTER below, produce one structured Markdown "note" in the EXACT format shown in the EXAMPLE. Separate consecutive notes with a line containing only:

===FILE: <Name>.md===

Output ONLY the notes (each preceded by its ===FILE: marker). No preamble, no closing summary, no commentary between notes.

# Field rules

- born / died: integer years. **Negative = BCE** (e.g. Plato born: -428). Use best scholarly consensus.
- uncertain: true if the dates are legendary or strongly contested (e.g. Laozi, the Buddha's traditional vs. revised dating), else false.
- birth_lat / birth_lon and active_lat / active_lon: decimal degrees of the **birthplace** and of the **place they mainly taught/worked** (these differ often — Aristotle born in Stagira, taught in Athens). This geography is critical: it's where each thinker sits on the globe.
- region: one broad band — one of: Greece, Rome, India, China, East Asia, Islamic world, Jewish, Europe, Americas.
- tradition: the school (e.g. Platonism, Stoicism, Madhyamaka Buddhism, Legalism).
- wikipedia: the full URL of their English Wikipedia article (used to fetch a portrait later).
- portrait: a direct image URL (Wikimedia Commons) of a portrait/bust if you are confident it is correct, else leave empty "".
- thesis: one sentence capturing their central claim.
- key_work: their most important work (title), or "".
- sources: 1–3 URLs backing the dates/biography.

# Edge rules (this is what draws the influence lines)

Use Obsidian-style [[Name]] wikilinks that reference OTHER thinkers by the SAME name as their note. Put each link under the section that types the relationship:

- ## Influenced by — people who shaped them (teachers, predecessors they drew on).
- ## Develops — a tradition/figure they systematically extended (e.g. Mencius develops [[Confucius]]).
- ## Disagreed with — opponents. Use :: to name the CRUX of disagreement, then — for a note. E.g. - [[Aristotle]] :: Are universals real? — Forms are immanent, not transcendent.
- ## Revives — ONLY for retrieving/reinterpreting a figure from **more than ~150 years earlier** (a deliberate look back across time, not a continuous lineage).
- ## Cruxes — the big questions they took a position on, as - [[Question?]] — their stance. Reuse the SAME crux wording across thinkers who addressed it, so debates link up (e.g. [[Is the self real?]], [[Are universals real?]], [[Is human nature good?]]).

You MAY link to thinkers not in this batch if the influence is real (they'll resolve later) — use the person's common English name.

# Idea travel (for the globe animation)

Add a ## Idea travel section: 2–5 bullet waypoints tracing how their key idea spread in space and time, each as - <year> — <place>: <what happened>. Years may be BCE (negative or "300 BCE"). Example for Buddhism: founding in the Gangetic plain, spread to Gandhara, transmission to China, etc.

# EXAMPLE (follow this format EXACTLY)

===FILE: Plato.md===
---
name: Plato
born: -428
died: -348
uncertain: false
birth_place: Athens, Greece
birth_lat: 37.98
birth_lon: 23.73
active_place: Athens, Greece
active_lat: 37.98
active_lon: 23.73
region: Greece
tradition: Platonism
wikipedia: https://en.wikipedia.org/wiki/Plato
portrait: https://upload.wikimedia.org/wikipedia/commons/5/5a/Plato_Silanion_Musei_Capitolini_MC1377.jpg
key_work: The Republic
thesis: The changing world of the senses is a shadow of eternal, unchanging Forms.
sources:
  - https://plato.stanford.edu/entries/plato/
  - https://en.wikipedia.org/wiki/Plato
---

# Plato

Founded the Academy in Athens. Recast Socrates' ethical questioning into a sweeping metaphysics in which true reality consists of eternal Forms, knowable by reason, of which the physical world is only a copy.

## Influenced by
- [[Socrates]] — his teacher; the dialectic and the priority of the soul
- [[Parmenides]] :: Is change real? — unchanging Being behind appearances
- [[Pythagoras]] — number, harmony, and the immortal soul

## Disagreed with
- [[Heraclitus]] :: Is change real? — flux applies only to the sensible world, not the Forms

## Cruxes
- [[Are universals real?]] — yes; the Forms exist independently of particulars

## Idea travel
- -387 — Athens: founds the Academy
- 250 — Rome/Alexandria: Platonism feeds Neoplatonism (Plotinus)
- 529 — Athens: Justinian closes the Academy; Platonist texts carried east into the Syriac/Islamic world
- 1462 — Florence: Ficino's Platonic Academy revives Plato in Renaissance Europe

# ROSTER (Batch A — antiquity)

Greece / Rome: Pythagoras, Heraclitus, Parmenides, Socrates, Plato, Aristotle, Epicurus, Zeno of Citium, Diogenes of Sinope, Plotinus
India: Mahavira, the Buddha (Siddhartha Gautama), Nagarjuna, Patanjali
China: Laozi, Confucius, Mozi, Mencius, Zhuangzi, Xunzi, Han Feizi

Produce all 21 notes now, each preceded by its ===FILE: <Name>.md=== marker, in the exact format above.
Show less
Thought for 27s
===FILE: Pythagoras.md===

name: Pythagoras
born: -570
died: -490
uncertain: false
birth_place: Samos, Greece
birth_lat: 37.75
birth_lon: 26.98
active_place: Croton, Magna Graecia
active_lat: 39.08
active_lon: 17.13
region: Greece
tradition: Pythagoreanism
wikipedia: https://en.wikipedia.org/wiki/Pythagoras

portrait: ""
key_work: ""
thesis: Reality is ordered by number, harmony, and the purification of the soul.
sources:

https://plato.stanford.edu/entries/pythagoras/

https://plato.stanford.edu/entries/pythagoreanism/

https://www.britannica.com/biography/Pythagoras

Pythagoras

Founded a religious-philosophical community at Croton. Later Pythagoreanism joined mathematics, music, cosmology, and the discipline of life into a vision of an ordered universe.

Influenced by

[[Thales]] — Ionian inquiry into nature and mathematics

[[Anaximander]] — cosmological speculation

[[Pherecydes of Syros]] — immortality and transmigration of the soul

Develops

[[Orphism]] — purification, ascetic practice, and the soul's journey

Disagreed with

[[Anaximander]] :: Is reality fundamentally numerical? — number and harmony, not the indefinite, order the cosmos

Cruxes

[[Is reality mathematical?]] — yes; number and ratio reveal the order of things

[[Is the soul immortal?]] — yes; the soul transmigrates and must be purified

Idea travel

-530 — Croton: founds a disciplined philosophical-religious community

-450 — Southern Italy: Pythagorean mathematics and soul-doctrine spread among Greek circles

-380 — Athens: Plato absorbs Pythagorean themes of number, harmony, and immortality

1462 — Florence: Renaissance Platonists revive Pythagorean number mysticism

===FILE: Heraclitus.md===

name: Heraclitus
born: -540
died: -480
uncertain: false
birth_place: Ephesus, Ionia
birth_lat: 37.94
birth_lon: 27.34
active_place: Ephesus, Ionia
active_lat: 37.94
active_lon: 27.34
region: Greece
tradition: Presocratic philosophy
wikipedia: https://en.wikipedia.org/wiki/Heraclitus

portrait: ""
key_work: On Nature
thesis: The cosmos is an ever-living order of change governed by the Logos.
sources:

https://plato.stanford.edu/entries/heraclitus/

https://iep.utm.edu/heraclit/

https://www.britannica.com/biography/Heraclitus

Heraclitus

An Ephesian aristocrat and obscure aphorist. He taught that conflict, opposition, and flux are not failures of order but the very structure of a rational cosmos.

Influenced by

[[Anaximander]] — Ionian cosmology and the search for an underlying order

[[Xenophanes]] — critique of conventional religion

Disagreed with

[[Pythagoras]] :: Is wisdom mathematical? — polymathy and number do not by themselves disclose the Logos

[[Parmenides]] :: Is change real? — change and opposition are real and ordered

Cruxes

[[Is change real?]] — yes; reality is ordered flux

[[Do opposites belong together?]] — yes; tension and opposition constitute harmony

Idea travel

-500 — Ephesus: composes aphorisms on Logos, fire, flux, and opposition

-390 — Athens: Plato frames Heraclitus as the thinker of becoming

250 — Rome/Alexandria: Stoics develop Logos and cosmic fire in Heraclitean terms

1807 — Jena: Hegel revives Heraclitus as a precursor of dialectic

===FILE: Parmenides.md===

name: Parmenides
born: -515
died: -450
uncertain: false
birth_place: Elea, Magna Graecia
birth_lat: 40.16
birth_lon: 15.16
active_place: Elea, Magna Graecia
active_lat: 40.16
active_lon: 15.16
region: Greece
tradition: Eleatic philosophy
wikipedia: https://en.wikipedia.org/wiki/Parmenides

portrait: ""
key_work: On Nature
thesis: What truly is cannot come to be, pass away, change, or be divided.
sources:

https://iep.utm.edu/parmenid/

https://plato.stanford.edu/entries/parmenides/

https://en.wikipedia.org/wiki/Parmenides

Parmenides

Founded the Eleatic challenge to ordinary experience. His poem forced later Greek philosophy to explain how change, plurality, and knowledge are possible if Being is one and ungenerated.

Influenced by

[[Xenophanes]] — critique of anthropomorphic religion and emphasis on unity

[[Pythagoras]] — southern Italian philosophical culture

Disagreed with

[[Heraclitus]] :: Is change real? — change is the illusion of mortal opinion

[[Pythagoras]] :: Is reality mathematical? — Being is prior to plurality and number

Cruxes

[[Is change real?]] — no; genuine Being is changeless

[[Can non-being be thought?]] — no; what is not cannot be thought or spoken

Idea travel

-475 — Elea: teaches the way of truth and the way of opinion

-450 — Elea/Athens: Zeno defends Eleatic monism with paradoxes

-370 — Athens: Plato makes Parmenides the central obstacle for metaphysics

1927 — Freiburg: Heidegger revives Parmenides in the question of Being

===FILE: Socrates.md===

name: Socrates
born: -470
died: -399
uncertain: false
birth_place: Athens, Greece
birth_lat: 37.98
birth_lon: 23.73
active_place: Athens, Greece
active_lat: 37.98
active_lon: 23.73
region: Greece
tradition: Socratic philosophy
wikipedia: https://en.wikipedia.org/wiki/Socrates

portrait: ""
key_work: ""
thesis: The examined life seeks virtue through relentless questioning of what one thinks one knows.
sources:

https://plato.stanford.edu/entries/socrates/

https://www.britannica.com/biography/Socrates

https://en.wikipedia.org/wiki/Socrates

Socrates

Left no writings. Through Plato, Xenophon, Aristophanes, and later tradition, he became the model of philosophy as ethical inquiry, public questioning, and care for the soul.

Influenced by

[[Anaxagoras]] — natural philosophy and the problem of mind

[[Parmenides]] :: Can virtue be known? — rigorous argument about what can be known

[[Sophists]] — public debate and ethical-political argument

Disagreed with

[[Sophists]] :: Is virtue teachable as technique? — rhetoric without truth corrupts the soul

[[Anaxagoras]] :: Does mind explain nature? — causal explanation must serve ethical understanding

Cruxes

[[Can virtue be known?]] — yes; virtue requires knowledge of the good

[[Is philosophy a way of life?]] — yes; inquiry should transform the soul

Idea travel

-430 — Athens: questions citizens in the agora

-399 — Athens: trial and execution make him a martyr of philosophical conscience

-385 — Athens: Plato's dialogues turn Socrates into the central figure of philosophy

1500 — Europe: Renaissance humanists revive Socratic moral inquiry

===FILE: Plato.md===

name: Plato
born: -428
died: -348
uncertain: false
birth_place: Athens, Greece
birth_lat: 37.98
birth_lon: 23.73
active_place: Athens, Greece
active_lat: 37.98
active_lon: 23.73
region: Greece
tradition: Platonism
wikipedia: https://en.wikipedia.org/wiki/Plato

portrait: https://upload.wikimedia.org/wikipedia/commons/5/5a/Plato_Silanion_Musei_Capitolini_MC1377.jpg

key_work: The Republic
thesis: The changing world of the senses is a shadow of eternal, unchanging Forms.
sources:

https://plato.stanford.edu/entries/plato/

https://en.wikipedia.org/wiki/Plato

Plato

Founded the Academy in Athens. Recast Socrates' ethical questioning into a sweeping metaphysics in which true reality consists of eternal Forms, knowable by reason, of which the physical world is only a copy.

Influenced by

[[Socrates]] — his teacher; the dialectic and the priority of the soul

[[Parmenides]] :: Is change real? — unchanging Being behind appearances

[[Pythagoras]] — number, harmony, and the immortal soul

Disagreed with

[[Heraclitus]] :: Is change real? — flux applies only to the sensible world, not the Forms

Cruxes

[[Are universals real?]] — yes; the Forms exist independently of particulars

Idea travel

-387 — Athens: founds the Academy

250 — Rome/Alexandria: Platonism feeds Neoplatonism through Plotinus

529 — Athens: Justinian closes the Academy; Platonist texts move east into Syriac and Islamic worlds

1462 — Florence: Ficino's Platonic Academy revives Plato in Renaissance Europe

===FILE: Aristotle.md===

name: Aristotle
born: -384
died: -322
uncertain: false
birth_place: Stagira, Chalcidice
birth_lat: 40.59
birth_lon: 23.79
active_place: Athens, Greece
active_lat: 37.98
active_lon: 23.73
region: Greece
tradition: Aristotelianism
wikipedia: https://en.wikipedia.org/wiki/Aristotle

portrait: ""
key_work: Metaphysics
thesis: Form is found in things themselves, and knowledge begins from the structured study of nature.
sources:

https://plato.stanford.edu/entries/aristotle/

https://www.britannica.com/biography/Aristotle

https://en.wikipedia.org/wiki/Aristotle

Aristotle

Studied at Plato's Academy, tutored Alexander, and founded the Lyceum. He systematized logic, biology, ethics, politics, poetics, and metaphysics into one of antiquity's most influential intellectual architectures.

Influenced by

[[Plato]] — teacher and chief philosophical point of departure

[[Socrates]] — ethical inquiry and definition

[[Parmenides]] :: Is change real? — the challenge of explaining change without contradiction

Develops

[[Plato]] — preserves the search for form and explanation while relocating form inside substances

Disagreed with

[[Plato]] :: Are universals real? — forms are immanent in things, not separate transcendent entities

[[Parmenides]] :: Is change real? — change is intelligible as the actualization of potential

Cruxes

[[Are universals real?]] — yes, but as forms instantiated in particulars

[[Is change real?]] — yes; change is the movement from potentiality to actuality

[[What is the good life?]] — flourishing through rational virtue

Idea travel

-335 — Athens: founds the Lyceum

-300 — Alexandria: Peripatetic inquiry feeds Hellenistic science

1150 — Toledo/Paris: Arabic-Latin translations carry Aristotle into medieval Europe

1250 — Paris: Scholasticism integrates Aristotle with Christian theology

===FILE: Epicurus.md===

name: Epicurus
born: -341
died: -270
uncertain: false
birth_place: Samos, Greece
birth_lat: 37.75
birth_lon: 26.98
active_place: Athens, Greece
active_lat: 37.98
active_lon: 23.73
region: Greece
tradition: Epicureanism
wikipedia: https://en.wikipedia.org/wiki/Epicurus

portrait: ""
key_work: Letter to Menoeceus
thesis: The good life is tranquil pleasure secured by friendship, modest desires, and freedom from fear.
sources:

https://plato.stanford.edu/entries/epicurus/

https://iep.utm.edu/epicur/

https://www.britannica.com/biography/Epicurus

Epicurus

Founded the Garden in Athens. He joined atomist physics to an ethics of ataraxia, arguing that fear of gods and death is the chief obstacle to happiness.

Influenced by

[[Democritus]] — atomism and natural explanation

[[Pyrrho]] — Hellenistic concern with tranquility

[[Aristippus]] — pleasure as an ethical starting point

Develops

[[Democritus]] — turns atomism into a therapy for fear and superstition

Disagreed with

[[Plato]] :: What is the good life? — happiness is not ascent to Forms but tranquil embodied life

[[Zeno of Citium]] :: What is the good life? — pleasure, not virtue alone, is the end

Cruxes

[[What is the good life?]] — tranquil pleasure, friendship, and freedom from fear

[[Should we fear death?]] — no; where we are, death is not, and where death is, we are not

[[Do gods govern the world?]] — no; gods do not providentially intervene in human life

Idea travel

-306 — Athens: founds the Garden

-50 — Rome: Lucretius spreads Epicurean atomism in De Rerum Natura

1417 — Germany/Italy: Poggio rediscovers Lucretius, helping revive Epicurean naturalism

1650 — Europe: early modern atomists adapt Epicurean physics

===FILE: Zeno of Citium.md===

name: Zeno of Citium
born: -334
died: -262
uncertain: false
birth_place: Citium, Cyprus
birth_lat: 34.92
birth_lon: 33.63
active_place: Athens, Greece
active_lat: 37.98
active_lon: 23.73
region: Greece
tradition: Stoicism
wikipedia: https://en.wikipedia.org/wiki/Zeno_of_Citium

portrait: ""
key_work: Republic
thesis: Happiness consists in living virtuously in agreement with nature and reason.
sources:

https://plato.stanford.edu/entries/stoicism/

https://en.wikipedia.org/wiki/Zeno_of_Citium

https://www.britannica.com/biography/Zeno-of-Citium

Zeno of Citium

Founded Stoicism in the painted porch at Athens. His school fused Socratic ethics, Cynic austerity, and a rational cosmology into a durable philosophy of virtue and self-command.

Influenced by

[[Socrates]] — moral seriousness and rational examination

[[Diogenes of Sinope]] — Cynic independence from convention

[[Crates of Thebes]] — teacher and Cynic model

[[Heraclitus]] — Logos, fire, and cosmic order

Develops

[[Diogenes of Sinope]] — transforms Cynic askesis into a systematic philosophy of logic, physics, and ethics

Disagreed with

[[Epicurus]] :: What is the good life? — virtue, not pleasure, is sufficient for happiness

[[Plato]] :: Are passions good guides? — passions are judgments to be disciplined by reason

Cruxes

[[What is the good life?]] — life according to nature and reason

[[Are passions good guides?]] — no; passions are mistaken judgments

[[Is the cosmos providential?]] — yes; the cosmos is rationally ordered by Logos

Idea travel

-300 — Athens: begins teaching at the Stoa Poikile

-150 — Rhodes/Rome: Stoicism enters Roman elite education

50 — Rome: Seneca and Musonius adapt Stoicism for imperial society

180 — Rome: Marcus Aurelius' Meditations becomes a later global Stoic touchstone

===FILE: Diogenes of Sinope.md===

name: Diogenes of Sinope
born: -412
died: -323
uncertain: false
birth_place: Sinope, Anatolia
birth_lat: 42.03
birth_lon: 35.15
active_place: Corinth, Greece
active_lat: 37.94
active_lon: 22.93
region: Greece
tradition: Cynicism
wikipedia: https://en.wikipedia.org/wiki/Diogenes

portrait: ""
key_work: ""
thesis: Freedom comes from rejecting artificial needs, social vanity, and corrupt convention.
sources:

https://iep.utm.edu/diogsino/

https://www.britannica.com/biography/Diogenes-Greek-philosopher

https://en.wikipedia.org/wiki/Diogenes

Diogenes of Sinope

The most famous Cynic, remembered through anecdotes of shameless simplicity, public provocation, and contempt for status. He made philosophy a visible performance of freedom from convention.

Influenced by

[[Antisthenes]] — Socratic austerity and virtue

[[Socrates]] — ethical independence and public questioning

Develops

[[Socrates]] — radicalizes the examined life into bodily, social, and political nonconformity

Disagreed with

[[Plato]] :: What is the good life? — virtue requires lived simplicity, not metaphysical theory

[[Aristotle]] :: Is politics natural? — conventional citizenship is secondary to cosmopolitan freedom

Cruxes

[[What is the good life?]] — radical self-sufficiency and freedom from convention

[[Is philosophy a way of life?]] — yes; philosophy must be embodied in practice

[[Is social status real?]] — no; status is a corrupt convention

Idea travel

-360 — Athens: Cynic performance-philosophy becomes notorious

-335 — Corinth: anecdotes with Alexander dramatize freedom before power

-300 — Athens: Zeno turns Cynic ethics into early Stoicism

1500 — Europe: Renaissance and Enlightenment writers revive Diogenes as a critic of hypocrisy

===FILE: Plotinus.md===

name: Plotinus
born: 205
died: 270
uncertain: false
birth_place: Lycopolis, Egypt
birth_lat: 27.18
birth_lon: 31.18
active_place: Rome, Roman Empire
active_lat: 41.90
active_lon: 12.50
region: Rome
tradition: Neoplatonism
wikipedia: https://en.wikipedia.org/wiki/Plotinus

portrait: ""
key_work: The Enneads
thesis: All reality emanates from the ineffable One and seeks return through intellect and contemplation.
sources:

https://plato.stanford.edu/entries/plotinus/

https://www.britannica.com/biography/Plotinus

https://en.wikipedia.org/wiki/Plotinus

Plotinus

Studied in Alexandria and taught in Rome. His Enneads transformed Plato into a late-antique metaphysics of emanation, hierarchy, and mystical return to the One.

Influenced by

[[Plato]] — Forms, the Good, and the ascent of the soul

[[Aristotle]] — metaphysics of intellect and substance

[[Ammonius Saccas]] — teacher in Alexandria

Develops

[[Plato]] — systematizes Platonism into One, Intellect, and Soul

Revives

[[Parmenides]] — retrieves the problem of the One across seven centuries

[[Plato]] — reinterprets classical Platonism more than five centuries later

Disagreed with

[[Aristotle]] :: Are universals real? — intelligible reality is higher than sensible substances

[[Gnosticism]] :: Is the material cosmos evil? — the world is lower than Intellect but still beautiful and ordered

Cruxes

[[Are universals real?]] — yes; intelligible reality is more real than sensible things

[[Is the self real?]] — the empirical self is lower than the soul's intelligible source

[[Is ultimate reality personal?]] — no; the One is beyond being and intellect

Idea travel

244 — Rome: begins teaching after study in Alexandria

270 — Rome: Porphyry edits Plotinus' writings into the Enneads

500 — Athens/Alexandria: Neoplatonism shapes late antique pagan and Christian philosophy

1462 — Florence: Ficino translates Plotinus, reviving Neoplatonism in Renaissance Europe

===FILE: Mahavira.md===

name: Mahavira
born: -599
died: -527
uncertain: true
birth_place: Kshatriyakundagrama, Bihar
birth_lat: 25.99
birth_lon: 85.13
active_place: Vaishali and Magadha, India
active_lat: 25.68
active_lon: 85.22
region: India
tradition: Jainism
wikipedia: https://en.wikipedia.org/wiki/Mahavira

portrait: ""
key_work: ""
thesis: Liberation comes through nonviolence, ascetic discipline, and freeing the soul from karmic bondage.
sources:

https://www.britannica.com/biography/Mahavira-Jaina-teacher

https://www.britannica.com/summary/Mahavira-Jaina-teacher

https://en.wikipedia.org/wiki/Mahavira

Mahavira

The twenty-fourth Tirthankara of Jain tradition. He organized an ascetic community around radical nonviolence, restraint, karma, and liberation of the soul.

Influenced by

[[Parshvanatha]] — earlier Jain Tirthankara and fourfold restraint tradition

[[Ajivikas]] — ascetic milieu of the Gangetic plain

Develops

[[Parshvanatha]] — expands Jain discipline into the five great vows

Disagreed with

[[the Buddha]] :: Is the self real? — the soul is real and must be liberated from karma

[[Makkhali Gosala]] :: Is moral effort effective? — liberation depends on disciplined action, not fatalism

Cruxes

[[Is the self real?]] — yes; the jiva is real and bound by karma

[[Does nonviolence have absolute priority?]] — yes; ahimsa is the supreme discipline

[[Can karma be burned away?]] — yes; austerity and restraint purify the soul

Idea travel

-527 — Pavapuri: traditional date of Mahavira's nirvana

-300 — Magadha: Jain monastic communities persist under Mauryan-era patronage

500 — Gujarat/Rajasthan: Jain mercantile and monastic networks expand westward

1200 — Western India: Jain scholasticism and temple culture flourish

===FILE: the Buddha (Siddhartha Gautama).md===

name: the Buddha (Siddhartha Gautama)
born: -563
died: -483
uncertain: true
birth_place: Lumbini, Nepal
birth_lat: 27.47
birth_lon: 83.28
active_place: Sarnath and the Gangetic Plain, India
active_lat: 25.38
active_lon: 83.02
region: India
tradition: Buddhism
wikipedia: https://en.wikipedia.org/wiki/The_Buddha

portrait: ""
key_work: ""
thesis: Suffering arises from craving and ceases through the Noble Eightfold Path.
sources:

https://www.britannica.com/biography/Buddha-founder-of-Buddhism

https://www.britannica.com/topic/Buddhism

https://en.wikipedia.org/wiki/The_Buddha

the Buddha (Siddhartha Gautama)

A wandering teacher of the eastern Gangetic plain. He rejected both indulgence and self-mortification, teaching a middle path of ethical conduct, meditation, insight, and liberation from suffering.

Influenced by

[[Alara Kalama]] — meditative training

[[Uddaka Ramaputta]] — formless meditative attainment

[[Mahavira]] — shared ascetic and renunciant milieu

Develops

[[Sramana movement]] — reworks renunciation around the middle way and dependent arising

Disagreed with

[[Mahavira]] :: Is the self real? — no permanent self can be found

[[Makkhali Gosala]] :: Is moral effort effective? — intentional action matters for liberation

Cruxes

[[Is the self real?]] — no; persons are impermanent aggregates without permanent self

[[What causes suffering?]] — craving and ignorance

[[Can liberation be achieved in life?]] — yes; nirvana is possible through the path

Idea travel

-528 — Bodh Gaya: traditional site of awakening

-500 — Sarnath: first sermon sets the wheel of Dharma in motion

-250 — Pataliputra/Sanchi: Ashokan patronage spreads Buddhism across South Asia

100 — Gandhara: Buddhist art and texts move along Central Asian trade routes

400 — China: translated sutras establish Buddhism as an East Asian tradition

===FILE: Nagarjuna.md===

name: Nagarjuna
born: 150
died: 250
uncertain: true
birth_place: South India
birth_lat: 16.57
birth_lon: 80.36
active_place: Amaravati, Andhra Pradesh
active_lat: 16.57
active_lon: 80.36
region: India
tradition: Madhyamaka Buddhism
wikipedia: https://en.wikipedia.org/wiki/Nagarjuna

portrait: ""
key_work: Mulamadhyamakakarika
thesis: All phenomena are empty of intrinsic nature because they arise dependently.
sources:

https://www.britannica.com/biography/Nagarjuna

https://www.britannica.com/summary/Nagarjuna

https://en.wikipedia.org/wiki/Nagarjuna

Nagarjuna

Founder of Madhyamaka philosophy. He used radical dialectic to show that all views collapse if they posit intrinsic existence, while preserving conventional truth and dependent arising.

Influenced by

[[the Buddha (Siddhartha Gautama)]] — dependent arising and the middle way

[[Prajnaparamita Sutras]] — emptiness and the bodhisattva path

[[Abhidharma]] — analytic Buddhist categories he critiques

Develops

[[the Buddha (Siddhartha Gautama)]] — makes dependent arising and emptiness philosophically explicit

Revives

[[the Buddha (Siddhartha Gautama)]] — retrieves the middle way across several centuries of Buddhist scholastic development

Disagreed with

[[Sarvastivada]] :: Do things have intrinsic nature? — dharmas do not possess svabhava

[[Nyaya]] :: Can reason establish ultimate foundations? — all foundational theses are empty

Cruxes

[[Is the self real?]] — no; self is empty like all dependently arisen phenomena

[[Do things have intrinsic nature?]] — no; emptiness is dependent arising

[[Can language state ultimate truth?]] — only indirectly; ultimate truth is reached through deconstructing views

Idea travel

150 — Andhra/South India: Madhyamaka arguments emerge in Mahayana circles

400 — Chang'an: Kumarajiva translates Nagarjuna into Chinese

625 — Tibet/Central Asia: Madhyamaka enters Himalayan Buddhist scholasticism

800 — East Asia: Sanlun, Tiantai, and Zen absorb emptiness doctrine

===FILE: Patanjali.md===

name: Patanjali
born: 150
died: 250
uncertain: true
birth_place: Unknown, India
birth_lat: 22.97
birth_lon: 78.66
active_place: India
active_lat: 22.97
active_lon: 78.66
region: India
tradition: Yoga
wikipedia: https://en.wikipedia.org/wiki/Patanjali

portrait: ""
key_work: Yoga Sutras
thesis: Liberation is achieved by stilling the fluctuations of consciousness through disciplined practice and detachment.
sources:

https://iep.utm.edu/yoga/

https://www.britannica.com/topic/Yoga-sutras

https://en.wikipedia.org/wiki/Yoga_Sutras_of_Patanjali

Patanjali

The attributed compiler of the Yoga Sutras. The work systematized yoga as a path of concentration, ethical discipline, meditative absorption, and discriminative insight.

Influenced by

[[Samkhya]] — purusha, prakriti, and discriminative knowledge

[[the Buddha (Siddhartha Gautama)]] — shared meditative and renunciant disciplines

[[Upanishads]] — liberation through inward realization

Develops

[[Samkhya]] — adds disciplined yogic practice and devotion to Ishvara to a dualist metaphysics

Disagreed with

[[Nagarjuna]] :: Is the self real? — purusha is real, unlike Buddhist no-self and emptiness

[[Charvaka]] :: Is liberation real? — liberation is the highest goal, not bodily pleasure

Cruxes

[[Is the self real?]] — yes; purusha is distinct from mind and matter

[[Can liberation be achieved in life?]] — yes; through disciplined yoga and discriminative insight

[[What causes suffering?]] — misidentification of consciousness with mental fluctuations

Idea travel

200 — India: Yoga Sutras systematize earlier yoga practices

500 — India: commentarial traditions join Yoga closely to Samkhya

1000 — South Asia: yoga concepts enter tantric and devotional milieus

1893 — Chicago: modern global yoga begins to spread through transnational Vedanta and yoga teachers

===FILE: Laozi.md===

name: Laozi
born: -571
died: -471
uncertain: true
birth_place: Ku County, Chu
birth_lat: 33.86
birth_lon: 115.48
active_place: Luoyang, Zhou
active_lat: 34.62
active_lon: 112.45
region: China
tradition: Daoism
wikipedia: https://en.wikipedia.org/wiki/Laozi

portrait: ""
key_work: Daodejing
thesis: The wise align with the Dao through noncoercive action, simplicity, and return.
sources:

https://www.britannica.com/biography/Laozi

https://en.wikipedia.org/wiki/Laozi

https://plato.stanford.edu/entries/daoism/

Laozi

The legendary founder of Daoism and alleged author of the Daodejing. Modern scholarship treats the text as composite, but its voice became central to Chinese metaphysics, politics, and spirituality.

Influenced by

[[Book of Changes]] — correlative cosmology and transformation

[[Early Zhou sages]] — idealized antiquity and noncoercive rule

Disagreed with

[[Confucius]] :: Is ritual central to order? — ritual and moralism are symptoms of lost Dao

[[Mozi]] :: Should society be engineered by standards? — artificial standards disturb natural simplicity

Cruxes

[[Is ritual central to order?]] — no; genuine order follows the Dao without coercion

[[Should rulers act forcefully?]] — no; the best rule practices wuwei

[[Can language state ultimate truth?]] — no; the Dao that can be spoken is not the constant Dao

Idea travel

-400 — Warring States China: Daodejing materials circulate

142 — Sichuan: Celestial Masters institutionalize religious Daoism

650 — Tang China: Laozi is elevated as imperial ancestor and Daoist scripture gains state prestige

700 — East Asia: Daoist ideas travel into Korea and Japan through texts, ritual, and medicine

===FILE: Confucius.md===

name: Confucius
born: -551
died: -479
uncertain: false
birth_place: Qufu, Lu
birth_lat: 35.60
birth_lon: 116.99
active_place: Qufu, Lu
active_lat: 35.60
active_lon: 116.99
region: China
tradition: Confucianism
wikipedia: https://en.wikipedia.org/wiki/Confucius

portrait: ""
key_work: Analects
thesis: Humane persons cultivate virtue through ritual, learning, filiality, and right relationships.
sources:

https://plato.stanford.edu/entries/confucius/

https://www.britannica.com/biography/Confucius

https://en.wikipedia.org/wiki/Confucius

Confucius

A teacher and ritual reformer of late Spring and Autumn China. His disciples preserved his sayings as the Analects, making him the core ancestor of the Ru tradition.

Influenced by

[[Duke of Zhou]] — ritual order and moral kingship

[[Book of Songs]] — ethical formation through classical learning

[[Early Zhou sages]] — the model of humane government

Develops

[[Duke of Zhou]] — turns Zhou ritual inheritance into a personal and political ethic

Disagreed with

[[Laozi]] :: Is ritual central to order? — ritual is necessary for humane cultivation

[[Mozi]] :: Should care be impartial? — graded love begins from family roles

Cruxes

[[Is ritual central to order?]] — yes; ritual shapes humane persons and stable society

[[Is human nature good?]] — not systematized; humans require learning and cultivation

[[Should care be impartial?]] — no; ethical care is graded through roles and family

Idea travel

-500 — Lu: Confucius teaches disciples through ritual, poetry, and moral questioning

-300 — China: Mencius and Xunzi systematize rival Confucian inheritances

-136 — Chang'an: Han state patronage elevates Confucian classics

600 — Korea/Japan/Vietnam: Confucian texts enter East Asian statecraft and education

===FILE: Mozi.md===

name: Mozi
born: -470
died: -391
uncertain: false
birth_place: Lu, Zhou China
birth_lat: 35.60
birth_lon: 116.99
active_place: Lu and Song, Zhou China
active_lat: 34.79
active_lon: 114.31
region: China
tradition: Mohism
wikipedia: https://en.wikipedia.org/wiki/Mozi

portrait: ""
key_work: Mozi
thesis: Social order requires impartial care, meritocratic government, frugality, and opposition to aggressive war.
sources:

https://plato.stanford.edu/entries/mohism/

https://iep.utm.edu/mozi/

https://en.wikipedia.org/wiki/Mozi

Mozi

Founded Mohism, one of the major organized schools of the Warring States. His followers developed ethics, logic, military defense, and political meritocracy around impartial benefit.

Influenced by

[[Confucius]] — inherited the problem of ritual order and humane government

[[Early Zhou sages]] — appeal to ancient models of rulership

Disagreed with

[[Confucius]] :: Should care be impartial? — care should be universal and impartial, not graded by kinship

[[Laozi]] :: Should society be engineered by standards? — explicit standards and institutions are necessary

[[Xunzi]] :: Is ritual central to order? — costly ritual and music waste resources

Cruxes

[[Should care be impartial?]] — yes; universal care best promotes social benefit

[[Is ritual central to order?]] — no; elaborate ritual is wasteful

[[Is aggressive war justified?]] — no; offensive war is morally wrong and socially harmful

Idea travel

-430 — Lu/Song: Mohist groups organize as disciplined ethical and technical communities

-350 — Warring States China: Mohists advise rulers on defense, merit, and anti-aggression

-221 — Qin China: Mohism declines after imperial unification

1895 — China/Japan: modern reformers revive Mozi as a rationalist and egalitarian thinker

===FILE: Mencius.md===

name: Mencius
born: -372
died: -289
uncertain: false
birth_place: Zou, Zhou China
birth_lat: 35.41
birth_lon: 116.97
active_place: Qi, Zhou China
active_lat: 36.82
active_lon: 118.30
region: China
tradition: Confucianism
wikipedia: https://en.wikipedia.org/wiki/Mencius

portrait: ""
key_work: Mencius
thesis: Human nature is good because every person has innate moral sprouts that must be cultivated.
sources:

https://plato.stanford.edu/entries/mencius/

https://www.britannica.com/biography/Mencius-Chinese-philosopher

https://en.wikipedia.org/wiki/Mencius

Mencius

The great classical defender of Confucian moral psychology. He argued that benevolent government rests on the innate moral tendencies of the human heart.

Influenced by

[[Confucius]] — humane government, ritual, and moral cultivation

[[Zisi]] — Confucian transmission traditionally linked to Mencius

Develops

[[Confucius]] — grounds Confucian ethics in innate moral sprouts and benevolent rule

Disagreed with

[[Mozi]] :: Should care be impartial? — impartial care ignores the moral priority of family affection

[[Xunzi]] :: Is human nature good? — human nature is originally good, not bad

[[Yang Zhu]] :: Is moral duty social? — private self-concern neglects righteousness

Cruxes

[[Is human nature good?]] — yes; moral sprouts are innate

[[Should care be impartial?]] — no; love properly begins with family and extends outward

[[Can tyrants be overthrown?]] — yes; a tyrant loses the Mandate of Heaven

Idea travel

-320 — Qi/Liang: Mencius advises rulers on humane government

200 — Han China: Mencian Confucianism becomes part of classical learning

1130 — Song China: Zhu Xi canonizes the Mencius among the Four Books

1400 — Korea/Japan/Vietnam: Mencian moral psychology spreads through Neo-Confucian education

===FILE: Zhuangzi.md===

name: Zhuangzi
born: -369
died: -286
uncertain: false
birth_place: Meng, Song
birth_lat: 34.65
birth_lon: 116.36
active_place: Meng, Song
active_lat: 34.65
active_lon: 116.36
region: China
tradition: Daoism
wikipedia: https://en.wikipedia.org/wiki/Zhuang_Zhou

portrait: ""
key_work: Zhuangzi
thesis: Freedom lies in wandering beyond fixed distinctions, rigid identities, and anxious striving.
sources:

https://plato.stanford.edu/entries/zhuangzi/

https://www.britannica.com/biography/Zhuangzi

https://en.wikipedia.org/wiki/Zhuang_Zhou

Zhuangzi

A playful and profound Daoist writer of the Warring States. The Zhuangzi uses parable, humor, and paradox to loosen fixed judgments and reveal spontaneous freedom.

Influenced by

[[Laozi]] — Dao, wuwei, and distrust of artificial distinctions

[[Hui Shi]] — paradox, disputation, and relativizing perspectives

Develops

[[Laozi]] — expands Daoist noncoercion into perspectival freedom and spiritual wandering

Disagreed with

[[Confucius]] :: Is ritual central to order? — ritual roles can imprison spontaneous life

[[Mozi]] :: Should society be engineered by standards? — fixed standards miss the fluidity of Dao

[[Hui Shi]] :: Can language state ultimate truth? — clever distinctions cannot capture the Dao

Cruxes

[[Can language state ultimate truth?]] — no; language is perspectival and limited

[[Is ritual central to order?]] — no; spontaneous accord exceeds ritual

[[Is the self real?]] — the fixed self is unstable and transformable

Idea travel

-320 — Song/Chu region: Zhuangzi stories circulate among Warring States literati

300 — China: xuanxue thinkers read Zhuangzi with Laozi and the Yijing

700 — Tang China: Zhuangzi becomes central to elite poetry, painting, and Daoist thought

1200 — East Asia: Chan/Zen traditions absorb Zhuangzian language of spontaneity

===FILE: Xunzi.md===

name: Xunzi
born: -310
died: -235
uncertain: true
birth_place: Zhao, Zhou China
birth_lat: 37.87
birth_lon: 112.55
active_place: Jixia Academy, Qi
active_lat: 36.82
active_lon: 118.30
region: China
tradition: Confucianism
wikipedia: https://en.wikipedia.org/wiki/Xunzi

portrait: ""
key_work: Xunzi
thesis: Human nature is bad, so virtue must be made through ritual, learning, and deliberate effort.
sources:

https://plato.stanford.edu/archives/fall2025/entries/xunzi/

https://www.britannica.com/topic/List-of-Chinese-Philosophers

https://en.wikipedia.org/wiki/Xunzi

Xunzi

A late Warring States Confucian systematizer. He defended ritual, hierarchy, language, and learning as human inventions that transform raw desires into civilization.

Influenced by

[[Confucius]] — ritual, learning, and cultivated virtue

[[Mencius]] — Confucian moral psychology as the position to revise

[[Mozi]] — concern with standards, order, and social utility

Develops

[[Confucius]] — makes ritual an artificial technology for transforming human nature

Disagreed with

[[Mencius]] :: Is human nature good? — human nature is bad; goodness is deliberate artifice

[[Laozi]] :: Should rulers act forcefully? — cultivated institutions, not natural spontaneity, create order

[[Zhuangzi]] :: Can language state ultimate truth? — names and distinctions can be rectified for social order

Cruxes

[[Is human nature good?]] — no; virtue is produced by learning and ritual

[[Is ritual central to order?]] — yes; ritual transforms desire into civilized conduct

[[Should society be engineered by standards?]] — yes; institutions and names must be deliberately ordered

Idea travel

-270 — Jixia Academy: Xunzi teaches in the major intellectual center of Qi

-240 — Chu/Qin: students including Han Feizi and Li Si carry his rigor into Legalist statecraft

-136 — Han China: Confucian state ideology absorbs Xunzian ritual and institutional themes

1100 — Song China: Neo-Confucians debate Xunzi against Mencian orthodoxy

===FILE: Han Feizi.md===

name: Han Feizi
born: -280
died: -233
uncertain: false
birth_place: Han state, Zhou China
birth_lat: 34.76
birth_lon: 113.65
active_place: Han and Qin courts, China
active_lat: 34.35
active_lon: 108.94
region: China
tradition: Legalism
wikipedia: https://en.wikipedia.org/wiki/Han_Fei

portrait: ""
key_work: Han Feizi
thesis: Stable rule depends on impersonal law, administrative technique, and positional power rather than moral virtue.
sources:

https://plato.stanford.edu/entries/chinese-legalism/

https://www.britannica.com/biography/Han-Feizi

https://en.wikipedia.org/wiki/Han_Fei

Han Feizi

A prince of Han and the great synthesizer of Legalism. He argued that rulers should rely on clear laws, bureaucratic methods, and institutional power instead of moral persuasion.

Influenced by

[[Xunzi]] — teacher; pessimistic view of raw human tendencies

[[Shang Yang]] — law, punishments, rewards, and state strengthening

[[Shen Buhai]] — administrative technique and bureaucratic control

[[Shen Dao]] — positional power and authority

Develops

[[Xunzi]] — turns the need for artificial order into a hard theory of state power

[[Shang Yang]] — integrates law with technique and ruler authority

Disagreed with

[[Confucius]] :: Is ritual central to order? — moral ritual is too weak for state order

[[Mencius]] :: Can virtue govern politics? — benevolence cannot reliably govern ministers and subjects

[[Mozi]] :: Should care be impartial? — public order requires law and power, not moralized care

Cruxes

[[Can virtue govern politics?]] — no; institutions must assume self-interest

[[Should society be engineered by standards?]] — yes; law and administrative technique must structure conduct

[[Is ritual central to order?]] — no; law is more reliable than ritual

Idea travel

-240 — Han/Qin: Han Feizi's writings circulate among Warring States rulers

-221 — Qin capital Xianyang: Legalist statecraft helps shape imperial unification

-206 — Han China: official ideology rejects Legalism while retaining many institutions

1900 — China: modern reformers revisit Legalism as a theory of state capacity

Instant
ChatGPT can make mistakes. Check important info.