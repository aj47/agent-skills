# Validation Output Schema

Reference schema for `validation_report.json` generated during Pass 2 (Narrative Validation).

## Overview

The validation report identifies:
1. **Detected narrative arcs** and their completeness
2. **Gaps** in story coverage
3. **Orphan beats** (claims without proof, results without setup)
4. **Suggested clips** to fill gaps

---

## Full Schema

```json
{
  "validation_summary": {
    "total_clips_pass1": 45,
    "narrative_arcs_detected": 8,
    "arcs_complete": 3,
    "arcs_with_gaps": 5,
    "gaps_detected": 12,
    "high_priority_gaps": 3,
    "medium_priority_gaps": 6,
    "low_priority_gaps": 3,
    "orphan_claims": 2,
    "orphan_resolutions": 1,
    "suggested_additional_clips": 7
  },

  "narrative_arcs": [
    {
      "id": "arc_001",
      "type": "ARGUMENT",
      "title": "Skills Can Replace MCPs",
      "completeness_score": 0.33,
      "status": "INCOMPLETE",
      "time_span": {
        "start": 342.5,
        "end": 538.5
      },
      "beats": {
        "CLAIM": {
          "found": true,
          "clip_id": "clip_023",
          "clip_index": 23,
          "timestamp_range": [342.5, 358.2],
          "text_preview": "My thesis is that skills can completely replace MCPs...",
          "confidence": 0.95
        },
        "EVIDENCE": {
          "found": false,
          "expected_range": [360.0, 520.0],
          "search_performed": true,
          "search_notes": "Demo content detected but not captured as clip"
        },
        "RESOLUTION": {
          "found": true,
          "clip_id": "clip_045",
          "clip_index": 45,
          "timestamp_range": [525.0, 538.5],
          "text_preview": "Boom! Same functionality. No MCP required. See?",
          "confidence": 0.94
        }
      },
      "optional_beats_found": ["STAKES"],
      "gaps": ["evidence_missing"],
      "gap_ids": ["gap_001"],
      "notes": "Core stream thesis - demo is critical for completeness"
    }
  ],

  "gaps": [
    {
      "id": "gap_001",
      "priority": "HIGH",
      "priority_score": 9,
      "type": "missing_evidence",
      "arc_id": "arc_001",
      "arc_type": "ARGUMENT",
      "timestamp_range": [375.0, 512.8],
      "duration": 137.8,
      "description": "Demo proving skills can replace MCPs",
      "why_important": "Stream titled 'Skills vs MCPs' - the demo IS the content. Without it, thesis is unsupported.",
      "content_detected": true,
      "content_description": "Live coding session building a skill to replicate MCP functionality",
      "suggested_clip": {
        "start_time": 375.0,
        "end_time": 512.8,
        "start_index": 152,
        "end_index": 189,
        "category": "teaching",
        "suggested_title": "Building a Skill to Replace MCPs - Live Demo",
        "reason": "Core evidence for stream thesis - demonstrates claim in action",
        "confidence": 0.85,
        "source": "narrative_validation",
        "beat_type": "EVIDENCE",
        "would_complete_arc": "arc_001"
      }
    },
    {
      "id": "gap_002",
      "priority": "MEDIUM",
      "priority_score": 5,
      "type": "missing_steps",
      "arc_id": "arc_003",
      "arc_type": "TUTORIAL",
      "timestamp_range": [1200.0, 1380.0],
      "duration": 180.0,
      "description": "OAuth configuration walkthrough",
      "why_important": "Result clip shows 'It works!' but setup process not captured",
      "content_detected": true,
      "content_description": "Step-by-step configuration of OAuth settings",
      "suggested_clip": {
        "start_time": 1200.0,
        "end_time": 1380.0,
        "category": "teaching",
        "suggested_title": "OAuth Configuration Walkthrough",
        "reason": "Complete the tutorial arc - show HOW not just result",
        "confidence": 0.75,
        "source": "narrative_validation",
        "beat_type": "STEPS",
        "would_complete_arc": "arc_003"
      }
    }
  ],

  "orphan_claims": [
    {
      "clip_id": "clip_078",
      "clip_index": 78,
      "claim_text": "I think Cursor is overrated compared to other editors",
      "timestamp": 4521.3,
      "beat_type": "CLAIM",
      "search_window": [4521.3, 4821.3],
      "search_result": "No EVIDENCE or RESOLUTION found within 5 minutes",
      "note": "Standalone opinion - may have value as hot take clip but lacks proof",
      "standalone_value": 0.72,
      "recommendation": "Keep as standalone opinion clip, flag as unsubstantiated"
    }
  ],

  "orphan_resolutions": [
    {
      "clip_id": "clip_092",
      "clip_index": 92,
      "resolution_text": "Yes! Finally working!",
      "timestamp": 5892.1,
      "beat_type": "CONFIRMATION",
      "search_window": [5592.1, 5892.1],
      "search_result": "No PROBLEM or FIX detected in preceding 5 minutes",
      "note": "Victory reaction without visible struggle/fix",
      "standalone_value": 0.65,
      "recommendation": "May need to extend clip backward to capture context"
    }
  ],

  "arc_coverage_matrix": {
    "stream_title_topics": ["skills", "mcps", "comparison", "demo"],
    "topics_covered": {
      "skills": true,
      "mcps": true,
      "comparison": true,
      "demo": false
    },
    "coverage_score": 0.75,
    "missing_critical_topics": ["demo"]
  },

  "suggested_clips": [
    {
      "source_gap": "gap_001",
      "start_time": 375.0,
      "end_time": 512.8,
      "duration": 137.8,
      "suggested_title": "Building a Skill to Replace MCPs - Live Demo",
      "category": "teaching",
      "narrative_role": "EVIDENCE",
      "parent_arc": "arc_001",
      "confidence": 0.85,
      "priority": "HIGH",
      "reason": "Completes ARGUMENT arc - provides proof for thesis claim"
    }
  ],

  "action_items": [
    {
      "priority": 1,
      "action": "ADD_CLIP",
      "gap_id": "gap_001",
      "message": "CRITICAL: Add demo clip (06:15 - 08:33) - this is the proof for 'Skills vs MCPs' thesis"
    },
    {
      "priority": 2,
      "action": "EXTEND_CLIP",
      "clip_id": "clip_092",
      "direction": "backward",
      "suggested_extension": 60,
      "message": "Consider extending clip_092 backward to capture the fix that led to this success"
    },
    {
      "priority": 3,
      "action": "FLAG_ORPHAN",
      "clip_id": "clip_078",
      "message": "Clip contains unsubstantiated claim - consider as hot take or search for supporting content"
    }
  ],

  "metadata": {
    "validation_timestamp": "2026-01-01T12:00:00Z",
    "templates_checked": ["ARGUMENT", "TUTORIAL", "DISCOVERY", "COMPARISON", "PROBLEM_SOLUTION"],
    "total_arcs_found": 8,
    "complete_arcs": 3,
    "partial_arcs": 5,
    "stream_title": "Skills Can't Replace MCPs — Let's Test That LIVE",
    "stream_duration": 6420.0,
    "pass1_clips_analyzed": 45
  }
}
```

---

## Field Descriptions

### validation_summary

| Field | Type | Description |
|-------|------|-------------|
| total_clips_pass1 | int | Clips detected in Pass 1 (signal detection) |
| narrative_arcs_detected | int | Story arcs found in transcript |
| arcs_complete | int | Arcs with all required beats |
| arcs_with_gaps | int | Arcs missing required beats |
| gaps_detected | int | Total missing beat instances |
| high_priority_gaps | int | Critical gaps (stream thesis, main content) |
| suggested_additional_clips | int | Clips suggested to fill gaps |

### narrative_arcs[]

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique arc identifier (arc_001, arc_002) |
| type | string | Template type (ARGUMENT, TUTORIAL, etc.) |
| title | string | Descriptive title for the arc |
| completeness_score | float | 0.0-1.0 based on beats found |
| status | string | COMPLETE, INCOMPLETE, or PARTIAL |
| beats | object | Map of beat types to their detection status |
| gaps | array | List of missing beat types |
| gap_ids | array | References to gap objects |

### gaps[]

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique gap identifier |
| priority | string | HIGH, MEDIUM, or LOW |
| priority_score | int | 1-10 numeric priority |
| type | string | missing_evidence, missing_steps, etc. |
| arc_id | string | Parent arc reference |
| timestamp_range | array | [start, end] in seconds |
| why_important | string | Human-readable explanation |
| suggested_clip | object | Suggested clip to fill gap |

### Priority Scoring

Priority scores are calculated as:

```
priority_score = (centrality * 3) + (references * 2) + (duration * 1) + (energy * 1)

Where:
- centrality: Is this the MAIN point? (1-3)
- references: How often is content referenced? (0-2)
- duration: How much content missing? (0-2)
- energy: Does gap contain high-energy moments? (0-2)
```

| Score | Priority |
|-------|----------|
| 7-10 | HIGH |
| 4-6 | MEDIUM |
| 1-3 | LOW |

---

## User Interaction Flow

### Presenting Gaps

When presenting gaps to user:

```
⚠️  NARRATIVE GAPS DETECTED

The following important content was NOT captured as clips:

1. [HIGH] "Skills vs MCPs Demo" (06:15 - 08:33)
   Your thesis claim and conclusion were clipped, but the DEMO proving
   the thesis was missed. This 2-minute segment shows the actual
   skill being built.

   → Suggest: Add as clip "Building a Skill to Replace MCPs - Live Demo"

2. [MEDIUM] "OAuth Configuration" (20:00 - 23:00)
   Clip #12 shows the result ("It works!") but the setup showing
   HOW it was configured is missing.

   → Suggest: Add as clip "OAuth Configuration Walkthrough"

Accept suggestions? [Y/n/select]
```

### User Responses

| Response | Action |
|----------|--------|
| Y / yes | Add ALL suggested clips to segments.json |
| n / no | Skip suggestions, proceed with current clips |
| select | Present numbered list for individual selection |
| 1,3,5 | Add only selected suggestions by number |

### After Approval

1. Merge approved suggestions into `segments.json`
2. Update arc status to COMPLETE where applicable
3. Recalculate compilations
4. Proceed to extraction

---

## Integration with segments.json

After validation, `segments.json` should include:

1. **story_arcs[]** array with complete arc information
2. **orphan_beats[]** array with orphan claims/resolutions
3. **narrative** object in each clip with beat_type, arc_id, etc.
4. Updated **metadata** with validation stats

See [SKILL.md](SKILL.md) for complete output format.
