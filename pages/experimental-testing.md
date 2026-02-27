---
title: Experimental Testing
description: Experimental campaign records for track and road material testing.
permalink: /experimental-testing/
redirect_from:
  - /experiment-testing
  - /experiment-testing/
  - /experiment-testing/index.html
  - /field-testing
  - /field-testing/
  - /field-testing/index.html
  - /sv/experimental-testing
  - /sv/experimental-testing/
  - /sv/experimental-testing/index.html
  - /sv/experiment-testing
  - /sv/experiment-testing/
  - /sv/experiment-testing/index.html
  - /sv/field-testing
  - /sv/field-testing/
  - /sv/field-testing/index.html
---

{% assign intro_block = site.blocks | where: 'slug', 'experimental_testing_intro' | first %}
{% if intro_block %}
<section class="card">
  {{ intro_block.content | markdownify }}
</section>
{% endif %}

<section style="margin-top: 1rem;">
{% assign grouped = site.data.experimental_testing | group_by_exp: "item", "item.year" | sort: "name" | reverse %}

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
</section>
