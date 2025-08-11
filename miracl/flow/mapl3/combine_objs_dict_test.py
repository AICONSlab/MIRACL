from miracl.seg.mapl3.mapl3_cli_parser_args import mapl3_object_dict as seg_mapl3_objs
from miracl.flow.mapl3.mapl3_workflow_cli_parser_args import (
    reg_object_dict as reg_mapl3_objs,
)

print(f"seg: {seg_mapl3_objs}")
print(f"reg: {reg_mapl3_objs}")

# Combine the MAPL3 objs dict with the registration objs dict
seg_mapl3_objs.update(reg_mapl3_objs)
combined = seg_mapl3_objs

print(f"combined: {combined}")
