# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from abc import abstractmethod
from typing import Text, Optional, Dict, Any, List
from typing import Tuple
from typing import Type

from ansible.errors import AnsibleLookupError
from ansible.parsing.dataloader import DataLoader
from ansible.plugins.lookup import LookupBase as AnsibleLookupBase
from ansible.template import Templar

from ..plugin_utils.args_validation import ValidateArgsResult, validate_args, \
    ValidateArgsSchema
from ..plugin_utils.execute_plugins import execute_lookup
from ..plugin_utils.path import append_collection_path_to_ansible_search_path


class LookupBase(AnsibleLookupBase):
    _loader = None  # type: DataLoader
    _templar = None  # type: Templar

    @abstractmethod
    def _run(self, terms, variables, **kwargs):
        # type: (LookupBase, List, Dict, **Dict) -> List
        """ Lookup Plugins should implement this method to perform their own business
        Method will be safely executed by C(LookupBase::run)
        """

    def _check_varspec(self, variables, schema, schema_format='doc'):
        # type: (LookupBase, Dict, ValidateArgsSchema, Text) -> ValidateArgsResult
        return validate_args(
            caller="Lookup %s" % self.__class__,
            args=variables,
            schema=schema,
            schema_format=schema_format
        )

    @classmethod
    def _format_vars_spec_validation_errors(cls, errors):
        # type: (Type[LookupBase], List) -> Text
        return 'Errors during variables validation => \n- %s' % "\n- ".join(errors)

    def __validate_variables(self, variables):
        # type: (LookupBase, Dict) -> Tuple[bool, Optional[Text], Dict]
        vars_spec = getattr(self, "VARIABLES_SPEC", None)
        if vars_spec is not None:
            self._display.display('vars_spec=%s' % vars_spec)
            valid, errors, valid_vars = self._check_varspec(variables=variables,
                                                            schema=dict(argument_spec=vars_spec),
                                                            schema_format='argspec')

            return valid, None if valid else self._format_vars_spec_validation_errors(errors), valid_vars

        return True, None, variables

    def _execute_lookup(self, name, terms, variables, **kwargs):
        # type: (LookupBase, Text, List, Dict, **Dict) -> Any
        loader_kwargs = dict(loader=self._loader, templar=self._templar)

        return execute_lookup(name, terms=terms, lookup_vars=variables, lookup_kwargs=kwargs,
                              loader_kwargs=loader_kwargs)

    def run(self, terms, variables=None, **kwargs):
        # type: (LookupBase, List, Optional[Dict], **Dict) -> List
        if variables is None:
            variables = dict()

        # Validated vars specification
        valid, error, valid_vars = self.__validate_variables(variables)

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
