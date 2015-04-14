from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.dispatch.adapters.base import AdapterBase
from ripozo.viewsets.relationships.list_relationship import ListRelationship

import json
import six

_content_type = 'application/hal+json'


class HalAdapter(AdapterBase):
    """
    An adapter that formats the response in the HAL format
    A description of the HAL format can be found here:
    `HAL Specification <http://stateless.co/hal_specification.html>`_
    """
    formats = ['hal', _content_type]

    @property
    def extra_headers(self):
        """
        :return: Just returns a single header for the Content-Type
        :rtype: dict
        """
        return {'Content-Type': _content_type}

    @property
    def formatted_body(self):
        """
        :return: The response body for the resource.
        :rtype: unicode
        """
        resource_url = self.combine_base_url_with_resource_url(self.resource.url)
        parent_properties = self.resource.properties.copy()

        embedded, links = self.generate_relationship(self.resource.relationships)
        embedded2, links2 = self.generate_relationship(self.resource.relationships)
        embedded.update(embedded2)
        links.update(links2)
        links.update(dict(self=dict(href=resource_url)))

        response = dict(_links=links, _embedded=embedded)
        response.update(parent_properties)
        return json.dumps(response)

    @staticmethod
    def generate_relationship(relationship_list):
        """
        Generates an appropriately formated embedded relationship
        in the HAL format.

        :param ripozo.viewsets.relationships.relationship.BaseRelationship relationship: The
            relationship that an embedded version is being created for.
        :return: If it is a ListRelationship it will return a list/collection of the
            embedded resources.  Otherwise it returns a dictionary as specified
            by the HAL specification.
        :rtype: list|dict
        """
        embedded_dict = {}
        links_dict = {}
        for relationship, field_name, embedded in relationship_list:
            if embedded:
                to_use = embedded_dict
            else:
                to_use = links_dict
            if isinstance(relationship, list):
                response = []
                for res in relationship:
                    if embedded:
                        response.append(res.properties)
                    else:
                        response.append(dict(href=res.url))
                to_use[field_name] = response
            elif embedded:
                to_use[field_name] = relationship.properties
            else:
                to_use[field_name] = dict(href=relationship.url)
        return embedded_dict, links_dict
