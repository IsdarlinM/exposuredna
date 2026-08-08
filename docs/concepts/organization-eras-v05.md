# Organization Eras in Exposure DNA 0.5

Organization Eras bound organization/asset relationships to explicit validity intervals so historical evidence is not silently projected into the present.

`relationship_at()` returns the relationship's evidenced status only when the query timestamp is inside its validity interval. Outside that interval the relationship becomes `UNKNOWN` for that point in time.

## Exclusive temporal conflicts

Some imported relationships may be explicitly marked `exclusive`. For `OWNS` and `OPERATES`, overlapping exclusive claims by different organizations against the same asset are emitted as an `UNKNOWN` temporal conflict with supporting and counter-evidence references.

Exposure DNA does not assume all ownership or operation is exclusive. Conflict detection therefore requires the explicit flag.

Temporal entity resolution cannot create `VALIDATED` ownership. Authoritative current evidence and human-controlled validation remain necessary.
