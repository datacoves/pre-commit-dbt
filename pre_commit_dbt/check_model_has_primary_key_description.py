import argparse
from typing import Any
from typing import Dict, List
from typing import Optional
from typing import Sequence

from pre_commit_dbt.utils import add_filenames_args
from pre_commit_dbt.utils import add_manifest_args
from pre_commit_dbt.utils import get_json
from pre_commit_dbt.utils import JsonOpenError
from pre_commit_dbt.utils import get_missing_file_paths
from pre_commit_dbt.utils import get_model_sqls
from pre_commit_dbt.utils import get_models
from pre_commit_dbt.utils import yellow


def check_primary_key_description(
        paths: Sequence[str], manifest: Dict[str, Any]
) -> int:
    paths = get_missing_file_paths(paths, manifest)

    status_code = 0
    sqls = get_model_sqls(paths, manifest)
    filenames = set(sqls.keys())
    missing: List[str] = []

    # get manifest nodes that pre-commit found as changed
    models = get_models(manifest, filenames)
    for model in models:
        models_missing_pkey = {
            model.model_name
            for key, value in model.node.get("columns", {}).items()
            if value['tags'] and 'primary-key' in value['tags'] and
            (not value['description'] or len(value['description']) < 2)  # checking for non-whitespace description value
        }
        if models_missing_pkey:
            missing.extend(models_missing_pkey)

    if missing:
        status_code = 1
        result = "\n- ".join(list(missing))
        print(
            f"Following models are missing primary-key description:\n- {yellow(result)}",
        )
    return status_code


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    add_filenames_args(parser)
    add_manifest_args(parser)

    args = parser.parse_args(argv)

    # Todo: Comment out this block to test.
    try:
        manifest = get_json(args.manifest)
    except JsonOpenError as e:
        print(f"Unable to load manifest file ({e})")
        return 1
    return check_primary_key_description(paths=args.filenames, manifest=manifest)


if __name__ == "__main__":
    exit(main())
