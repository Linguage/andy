---
title: Home
description: Research profile and publication archive for Andreas Andersson.
permalink: /
redirect_from:
  - /sv
  - /sv/
  - /sv/index.html
---

{% assign home_intro = site.blocks | where: 'slug', 'home_intro' | first %}

<section class="home-top-grid" aria-label="Profile summary" style="margin-top: 1rem;">
  <aside class="card home-side-card">
    <img class="profile-photo" src="https://www.kth.se/files/avatar/adde" alt="Andreas Andersson portrait" loading="lazy">
    <h2>External profiles</h2>
    <ul class="link-list">
      {% for profile in site.data.external_profiles %}
        <li><a href="{{ profile.url }}">{{ profile.label }}</a></li>
      {% endfor %}
    </ul>
  </aside>

  {% if home_intro %}
  <section class="card home-intro-card">
    {{ home_intro.content | markdownify }}
  </section>
  {% endif %}
</section>

<section class="grid-cards" aria-label="Core sections" style="margin-top: 1rem;">
  <article class="card">
    <p class="kicker">Publications</p>
    <h2>Searchable publication archive</h2>
    <p>Browse theses, journal papers, conference papers, and reports with filters by keyword, year, and type.</p>
    <a class="cta" href="{{ '/publications/' | relative_url }}">Open publications</a>
  </article>
  <article class="card">
    <p class="kicker">Teaching</p>
    <h2>Supervision and courses</h2>
    <p>Overview of PhD and master supervision plus current course contributions.</p>
    <a class="cta" href="{{ '/teaching/' | relative_url }}">Open teaching</a>
  </article>
  <article class="card">
    <p class="kicker">Projects</p>
    <h2>Research projects and commissions</h2>
    <p>Current projects in roads and railways with selected roles and commissions of trust.</p>
    <a class="cta" href="{{ '/projects/' | relative_url }}">Open projects</a>
  </article>
  <article class="card">
    <p class="kicker">Experimental Testing</p>
    <h2>Campaign log by year</h2>
    <p>Chronological record of in-situ dynamic testing activities across Sweden.</p>
    <a class="cta" href="{{ '/experimental-testing/' | relative_url }}">Open experimental testing</a>
  </article>
</section>

<section class="card" style="margin-top: 1rem;">
  <h2>Latest publications</h2>
  {% assign latest = site.data.publications | sort: 'year' | reverse %}
  <ul class="clean-list">
    {% for pub in latest limit: 6 %}
      <li>
        <strong>{{ pub.year }}</strong> - {{ pub.title }}
        <div class="meta">{{ pub.venue }}</div>
      </li>
    {% endfor %}
  </ul>
</section>
