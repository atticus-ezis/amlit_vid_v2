
You are writing a children's YouTube script in the YAML format shown below. 
Follow the rules and study the examples carefully — the examples demonstrate 
how to pick reference_image_keys and how to split `description` from `prompt`.

═══════════════════════════════════════════════════════════════════════
RULES
═══════════════════════════════════════════════════════════════════════

DURATION
- Sum of all scene `duration` values ≤ 150 seconds
- Each scene: 5–15 seconds
- 8–13 scenes total
- Narration + dialogue word count per scene ≤ (duration × 2.5)

CONTENT (children ages 4–8)
- Vocabulary at 1st–3rd grade level
- Sentences under 12 words, present tense, active voice
- No violence, death, or frightening imagery — soften dark plot points
- Include 1–2 onomatopoeia across the script ("Knock knock!", "Swoosh!")
- Include one short repeating refrain across 2–3 scenes
- Scene 1 opens with a hook in the first sentence
- Final scene ends on a warm, positive beat

NAMING
- Every scene `key` is unique, snake_case, describes the beat
- Character and background keys in design_sheets are snake_case and values are human-readable names. Example: "little_red_riding_hood: "Little Red Riding Hood"
- reference_image_keys must resolve to either a design_sheet key OR a 
prior scene `key`

REFERENCE IMAGE SELECTION (max 3)
For each scene, run this procedure:
1. List every visual element in the scene (characters, location, key props).
2. For each element, pick the freshest source:
  - First appearance → use the design_sheet key
  - Returning element → use the most recent prior scene where it appears 
    in the state you want (with current props, costume, mood)
  - Dramatic state change → fall back to the design_sheet key and 
    describe the new state in `description`/`prompt`
3. If two elements resolve to the same reference, that's one slot — you 
  gain a slot back.
4. Cap at 3. Priority order when trimming:
  active/speaking character → location → other characters → props
5. Prefer compounding (referencing prior scenes) over sheet references 
  once continuity is established — it preserves rendered detail.

DESCRIPTION vs IMAGE_PROMPT vs VIDEO_PROMPT
- `description`: 1–2 plain sentences of story-continuity narrative. What 
is happening in this beat, what state characters end in. No camera, no 
style language. This is what the NEXT scene reads to reason about state.
- `image_prompt`: DALL·E instructions for the still frame. Format:
  [shot type], [subject + action], [expression], [lighting/mood], 
  [new props or state changes].
Do NOT re-describe character appearance or location — the references 
carry that. Only describe what is NEW or DIFFERENT from the references.
- `video_prompt`: Video generation instructions. Describe camera movement,
  character motion, and ambient animation. Reference the composed image 
  implicitly — do not re-describe static appearance. Format:
  [camera behavior], [character/subject motion], [lighting/mood], 
  [ambient detail].

═══════════════════════════════════════════════════════════════════════
EXAMPLES (Little Red Riding Hood)
═══════════════════════════════════════════════════════════════════════

# EXAMPLE 1 — First appearance of character + location.
# Both elements are new, so both references come from design_sheets.

- sequence: 1
key: meet_little_red
duration: 7
narration: "Deep in a sunny village lived a happy girl in a red velvet hood. Everyone called her Little Red Riding Hood!"
description: "Little Red Riding Hood walks through her village smiling and waving to neighbors. She is cheerful and carries nothing yet."
image_prompt: "Wide shot, Little Red Riding Hood skipping down a village lane waving to two neighbors, bright joyful smile, warm morning sunlight."
video_prompt: "Camera holds wide as Little Red Riding Hood skips down the lane, waving cheerfully to neighbors. Warm morning sunlight, gentle sway in her hood and dress."
reference_image_keys:
  - little_red_riding_hood
  - home_village
dialogue: []

# EXAMPLE 2 — Returning character (LRRH) gains a new prop (the basket).
# We reference the PRIOR SCENE for LRRH, not the sheet — this locks her 
# rendered look. Mother is new → sheet. Location is the same village → we 
# could re-reference home_village, but `meet_little_red` already shows the 
# village, so it's doing double duty. Slot freed up for `mother`.

- sequence: 2
key: mothers_errand
duration: 9
narration: "One morning, her mother gave her a basket of cake and medicine. 'Take this to Grandma,' she said."
description: "On the porch of their cottage, Mother hands Little Red Riding Hood a wicker basket covered with a checkered cloth. Little Red Riding Hood now carries the basket."
image_prompt: "Medium shot on a cottage porch, Mother handing a wicker basket with a red checkered cloth to Little Red Riding Hood, both smiling warmly, soft morning light."
video_prompt: "Camera holds on a medium shot as Mother extends the basket toward Little Red Riding Hood, who reaches out to take it. Both smile. Soft morning light, subtle leaf movement in background."
reference_image_keys:
  - meet_little_red
  - mother
dialogue:
  mother: "Take this to Grandma. Stay on the path, and don't talk to strangers."

# EXAMPLE 3 — Multi-character at a new location.
# LRRH is established with basket in scene 2 → reference `mothers_errand`. 
# Wolf is new → sheet. Forest is new → sheet. That's exactly 3 refs, all 
# load-bearing. Notice the prompt doesn't describe LRRH's outfit or the 
# wolf's design — the references handle it.

- sequence: 4
key: meets_wolf
duration: 11
narration: "Skip, skip, skip down the path! Suddenly, a sneaky wolf stepped out from behind a tree."
description: "On the forest trail, Little Red Riding Hood pauses with her basket as the Wolf emerges from behind a tree with a sly grin. She is curious, not scared."
image_prompt: "Medium shot on a forest path, Little Red Riding Hood pausing with her basket, eyes wide with curiosity, the Wolf stepping out from behind a tree on the right with a sly toothy smile, dappled afternoon light through leaves."
video_prompt: "Camera holds medium as the Wolf slowly steps out from behind the tree. Little Red Riding Hood turns toward him, curious. Dappled afternoon light, leaves shifting gently overhead."
reference_image_keys:
  - mothers_errand
  - wolf
  - forest_trail
dialogue:
  wolf: "Hello there! Where are you going on this fine day?"

# EXAMPLE 4 — Compounding continuity, zero sheet references.
# LRRH arriving at Grandma's house. LRRH + basket → reference the most 
# recent scene with that state. Grandma's house exterior was established 
# in an earlier scene `wolf_at_grandmas` → reference that for the location 
# AND the wolf-inside state. Two references doing the work of three 
# elements (LRRH, basket, house, wolf-hiding-inside). Third slot unused.

- sequence: 7
key: red_arrives_at_house
duration: 8
narration: "Knock, knock! Little Red Riding Hood reached Grandma's cozy cottage."
description: "Little Red Riding Hood stands at Grandma's front door holding her basket, knocking gently. She doesn't know the Wolf is hiding inside."
image_prompt: "Medium shot at a cottage front door, Little Red Riding Hood knocking gently with one hand while holding her basket, a small curious smile, soft late-morning light."
video_prompt: "Camera holds medium as Little Red Riding Hood raises her hand and knocks on the door twice, basket swaying slightly at her side. Soft late-morning light, still and quiet."
reference_image_keys:
  - mothers_errand
  - wolf_at_grandmas
dialogue:
  little_red_riding_hood: "Grandma, it's me! I brought you cake."

═══════════════════════════════════════════════════════════════════════
NOW WRITE THE FULL SCRIPT FOR THE STORY BELOW.
Output valid YAML matching the format exactly. Nothing else.
═══════════════════════════════════════════════════════════════════════

STORY: {{insert story here}}

