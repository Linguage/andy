---
title: Publications
description: Filterable publications list by keyword, year, and type.
permalink: /publications/
redirect_from:
  - /sv/publications
  - /sv/publications/
  - /sv/publications/index.html
---

{% assign intro_block = site.blocks | where: 'slug', 'publications_intro' | first %}
{% assign years = site.data.publications | map: 'year' | uniq | sort | reverse %}

{% if intro_block %}
<section class="card">
  {{ intro_block.content | markdownify }}
</section>
{% endif %}

<form id="pub-filter-form" class="filter-panel" aria-label="Publication filters" style="margin-top: 1rem;">
  <div>
    <label for="filter-q">Keyword</label>
    <input id="filter-q" name="q" type="search" placeholder="e.g. concrete, resilience, compaction">
  </div>
  <div>
    <label for="filter-year">Year</label>
    <select id="filter-year" name="year">
      <option value="">All years</option>
      {% for year in years %}
        <option value="{{ year }}">{{ year }}</option>
      {% endfor %}
    </select>
  </div>
  <div>
    <label for="filter-type">Type</label>
    <select id="filter-type" name="type">
      <option value="">All types</option>
      <option value="thesis">Thesis</option>
      <option value="manuscript">Manuscript</option>
      <option value="journal">Journal paper</option>
      <option value="conference">Conference paper</option>
      <option value="chapter">Book chapter</option>
      <option value="report_trita">TRITA report</option>
      <option value="report_kth">KTH report</option>
    </select>
  </div>
</form>

<p class="filter-status"><span id="filter-count">0</span> publications shown.</p>
<p id="filter-empty" class="filter-status" hidden>No publication matched the current filter.</p>

{% assign publications = site.data.publications | sort: 'year' | reverse %}
<div class="pub-list" aria-live="polite">
  {% for pub in publications %}
    {% case pub.type %}
      {% when 'thesis' %}{% assign type_label = 'Thesis' %}
      {% when 'manuscript' %}{% assign type_label = 'Manuscript' %}
      {% when 'journal' %}{% assign type_label = 'Journal paper' %}
      {% when 'conference' %}{% assign type_label = 'Conference paper' %}
      {% when 'chapter' %}{% assign type_label = 'Book chapter' %}
      {% when 'report_trita' %}{% assign type_label = 'TRITA report' %}
      {% when 'report_kth' %}{% assign type_label = 'KTH report' %}
      {% else %}{% assign type_label = pub.type %}
    {% endcase %}
    {% assign authors = pub.authors | split: ';' %}
    {% assign author_text = authors | join: ', ' %}
    {% assign search_blob = pub.title | append: ' ' | append: pub.authors | append: ' ' | append: pub.venue | append: ' ' | append: pub.tags | append: ' ' | append: pub.links %}
    {% assign citation_text = author_text | append: ' (' | append: pub.year | append: '). ' | append: pub.title | append: '. ' | append: pub.venue | append: '.' %}
    {% assign query = pub.title | uri_escape %}
    {% assign fallback_links = 'scholar|https://scholar.google.com/scholar?q=' | append: query | append: ';diva|https://kth.diva-portal.org/smash/resultList.jsf?searchType=SIMPLE&query=' | append: query %}
    {% assign query_links = 'scholar|https://scholar.google.com/scholar?q=' | append: query | append: ';diva|https://kth.diva-portal.org/smash/resultList.jsf?searchType=SIMPLE&query=' | append: query %}
    <article class="pub-card" data-year="{{ pub.year }}" data-type="{{ pub.type }}" data-search="{{ search_blob | downcase | escape }}">
      <h3>{{ pub.title }}</h3>
      <p class="meta">{{ author_text }} | {{ pub.venue }} | {{ pub.year }}</p>
      <div class="pub-meta-row">
        <span class="pub-chip">{{ type_label }}</span>
        {% if pub.links != '' %}
          {% assign merged_links = pub.links | append: ';' | append: query_links %}
          {% include item_links.html links=merged_links %}
        {% else %}
          {% include item_links.html links=fallback_links %}
        {% endif %}
        <div class="pub-actions">
          <button type="button" class="copy-citation-btn" data-citation="{{ citation_text | escape }}">Copy citation</button>
        </div>
      </div>
    </article>
  {% endfor %}
</div>

<script src="{{ '/assets/js/publications.js' | relative_url }}" defer></script>
