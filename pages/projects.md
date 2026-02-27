---
title: Projects
description: Research projects and commission of trust.
permalink: /projects/
redirect_from:
  - /sv/projects
  - /sv/projects/
  - /sv/projects/index.html
---

{% assign intro_block = site.blocks | where: 'slug', 'projects_intro' | first %}
{% if intro_block %}
<section class="card">
  {{ intro_block.content | markdownify }}
</section>
{% endif %}

<section class="card" style="margin-top: 1rem;">
  <h2>Research Projects</h2>
  <ul class="clean-list">
    {% for project in site.data.projects_research %}
      <li>
        <strong>{{ project.year }}</strong> - {{ project.title }}
        <div class="meta">{{ project.description }}</div>
        {% include item_links.html links=project.links %}
      </li>
    {% endfor %}
  </ul>
</section>

<section class="card" style="margin-top: 1rem;">
  <h2>Commission of Trust</h2>
  <ul class="clean-list">
    {% for item in site.data.projects_commission %}
      <li>
        <strong>{{ item.period }}</strong> - {{ item.title }}
        {% include item_links.html links=item.links %}
      </li>
    {% endfor %}
  </ul>
</section>
