# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import os.path
from abc import abstractmethod

from ansible.errors import AnsibleLookupError
from ansible.parsing.dataloader import DataLoader
from ansible.plugins.lookup import LookupBase as AnsibleLookupBase
from ansible.template import Templar

from ..plugin_utils.execute_plugins import execute_lookup
from ..plugin_utils.args_validation import check_plugin_argspec

# Hack to avoid loading "typing" module at runtime (issue with sanity tests on python 2.7) while keeping MyPy happy
MYPY = False
if MYPY:
    from typing import Text, Optional, Dict, Any, List, Tuple, Type
    from ..plugin_utils.args_validation_typing import (
        ArgSpecSchema,
        ArgSpecOptionalSchema,
        PluginArgSpecReturn,
        ArgSpecSchema,
    )


class LookupBase(AnsibleLookupBase):
    _loader = None  # type: DataLoader
    _templar = None  # type: Templar

    VARIABLES_SPEC = None  # type: Optional[Dict]

    def run(self, terms, variables=None, **kwargs):
        # type: (LookupBase, List, Optional[Dict], **Dict) -> List
        if variables is None:
            variables = dict()

        # Validated vars specification
        valid, error, valid_vars = self.__validate_vars(variables)

        # Early return in case there is already a failure
        if not valid:
            raise AnsibleLookupError(error)

        # Execute internal method
        # try:
        return self._run(terms=terms, variables=valid_vars, **kwargs)
        # except Exception as exc:
        #    self._display.error('Error occurred during lookup execution: %s' % exc)
        #    raise AnsibleLookupError(to_text(exc))

        # return result

    @abstractmethod
    def _run(self, terms, variables, **kwargs):
        # type: (LookupBase, List, Dict, **Dict) -> List
        """ Lookup Plugins should implement this method to perform their own business
        Method will be safely executed by C(LookupBase::run)
        """

    def check_argspec(
        self,  # type: LookupBase
        args,  # type: Dict
        schema,  # type: ArgSpecSchema
        schema_format='doc',  # type: Text
        schema_conditionals=None,  # type: ArgSpecOptionalSchema
        other_args=None  # type: ArgSpecOptionalSchema
    ):
        # type: (...) -> PluginArgSpecReturn
        return check_plugin_argspec(
            " %s lookup" % os.path.basename(__file__),
            args,
            schema,
            schema_format,
            schema_conditionals,
            other_args
        )

    @classmethod
    def _format_vars_spec_validation_errors(cls, errors):
        # type: (Type[LookupBase], List) -> Text
        return 'Errors during variables validation => \n- %s' % "\n- ".join(errors)

    def __validate_vars(self, variables):
        # type: (LookupBase, Dict) -> Tuple[bool, Optional[List[Text]], Dict]
        vars_spec = self.VARIABLES_SPEC
        if vars_spec is not None:
            check_res, valid_vars = self.check_argspec(args=variables,
                                                       schema=dict(argument_spec=vars_spec),
                                                       schema_format='argspec')
            valid = not check_res['failed']

            return valid, None if valid else check_res['errors'], valid_vars

        return True, None, variables

    def _execute_lookup(self, name, terms, variables, **kwargs):
        # type: (LookupBase, Text, List, Dict, **Dict) -> Any
        loader_kwargs = dict(loader=self._loader, templar=self._templar)

        return execute_lookup(name, terms=terms, lookup_vars=variables, lookup_kwargs=kwargs,
                              loader_kwargs=loader_kwargs)
