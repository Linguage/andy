---
title: Field Testing
description: Field campaign records for track and road material testing.
permalink: /field-testing/
redirect_from:
  - /sv/field-testing
  - /sv/field-testing/
  - /sv/field-testing/index.html
---

{% assign intro_block = site.blocks | where: 'slug', 'field_testing_intro' | first %}
{% if intro_block %}
<section class="card">
  {{ intro_block.content | markdownify }}
</section>
{% endif %}

{% assign grouped = site.data.field_testing | group_by_exp: "item", "item.year" | sort: "name" | reverse %}

{% for group in grouped %}
  <details class="year-group" {% if forloop.first %}open{% endif %}>
    <summary>{{ group.name }}</summary>
    <ul class="clean-list">
      {% assign entries = group.items | sort: 'date' | reverse %}
      {% for entry in entries %}
        <li>
          <strong>{{ entry.date }}</strong> - {{ entry.title }}, {{ entry.location }}
          <div class="meta">{{ entry.notes }}</div>
          {% include item_links.html links=entry.links %}
        </li>
      {% endfor %}
    </ul>
  </details>
{% endfor %}
