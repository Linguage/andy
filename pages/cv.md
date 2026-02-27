---
title: CV
description: Employment, awards, and profile overview.
permalink: /cv/
redirect_from:
  - /sv/cv
  - /sv/cv/
  - /sv/cv/index.html
---

{% assign summary_block = site.blocks | where: 'slug', 'cv_summary' | first %}
{% assign general = site.data.cv_general | first %}

{% if summary_block %}
<section class="card">
  {{ summary_block.content | markdownify }}
</section>
{% endif %}

<section class="card" style="margin-top: 1rem;">
  <h2>General</h2>
  <ul class="clean-list">
    <li><strong>Affiliation:</strong> {{ general.affiliation }}</li>
    <li><strong>Department:</strong> {{ general.department }}</li>
    <li><a href="{{ general.profile_url }}">KTH profile</a></li>
  </ul>
</section>

<section class="grid-cards" style="margin-top: 1rem;">
  <article class="card">
    <h2>Employments</h2>
    <ul class="clean-list">
      {% for item in site.data.cv_employments %}
        <li>
          <strong>{{ item.period }}</strong> - {{ item.title }}
          <div class="meta">{{ item.org }}</div>
          {% include item_links.html links=item.links %}
        </li>
      {% endfor %}
    </ul>
  </article>

  <article class="card">
    <h2>Awards & Scholarships</h2>
    <ul class="clean-list">
      {% for item in site.data.cv_awards %}
        <li>
          <strong>{{ item.year }}</strong> - {{ item.item }}
          {% include item_links.html links=item.links %}
        </li>
      {% endfor %}
    </ul>
  </article>
</section>
