---
title: Teaching
description: Supervision and teaching portfolio.
permalink: /teaching/
redirect_from:
  - /sv/teaching
  - /sv/teaching/
  - /sv/teaching/index.html
---

{% assign intro_block = site.blocks | where: 'slug', 'teaching_intro' | first %}
{% if intro_block %}
<section class="card">
  {{ intro_block.content | markdownify }}
</section>
{% endif %}

<section class="grid-cards" style="margin-top: 1rem;">
  <article class="card">
    <h2>PhD Students</h2>
    <ul class="clean-list">
      {% for student in site.data.teaching_phd %}
        <li>
          <strong>{{ student.name }}</strong>
          <div class="meta">{{ student.status }} ({{ student.period }})</div>
          {% include item_links.html links=student.links %}
        </li>
      {% endfor %}
    </ul>
  </article>

  <article class="card">
    <h2>Master Students</h2>
    <ul class="clean-list">
      {% for student in site.data.teaching_master %}
        <li>
          <strong>{{ student.name }}</strong>
          <div class="meta">{{ student.status }} ({{ student.period }})</div>
          {% include item_links.html links=student.links %}
        </li>
      {% endfor %}
    </ul>
  </article>
</section>

<section class="card" style="margin-top: 1rem;">
  <h2>Courses</h2>
  <ul class="clean-list">
    {% for course in site.data.teaching_courses %}
      <li>
        <strong>{{ course.code }}</strong> - {{ course.name }}
        <div class="meta">{{ course.role }}</div>
        {% include item_links.html links=course.links %}
      </li>
    {% endfor %}
  </ul>
</section>
