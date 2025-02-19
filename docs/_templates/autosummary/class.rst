{{ name | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :show-inheritance:

   {% block attributes %}
   {% if attributes %}
   .. rubric:: {{ _('Attributes') }}

   {% for item in attributes %}
   {% if item not in inherited_members and not item.startswith('__') %}
   .. autoattribute:: {{ name }}.{{ item }}
   {% endif %}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block methods %}

   {% if methods %}
   .. rubric:: {{ _('Methods') }}

   {% if 'enums' not in fullname %}
   .. automethod:: {{ name }}.__init__
   {% endif %}

   {% for item in members %}
   {% if item not in attributes and item not in inherited_members %}
   .. automethod:: {{ name }}.{{ item }}
   {% endif %}
   {%- endfor %}

   {% endif %}
   {% endblock %}
