---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
---

# Unruly Objects

## Things

<ul>
  {% for thing in site.things %}
    <li>
      <a href="{{ site.baseurl }}{{ thing.url }}">{{ thing.thinglabel }}</a>
    </li>
  {% endfor %}
</ul>

## Dimensions

<ul>
  {% for dimension in site.dimensions %}
    <li>
      <a href="{{ site.baseurl }}{{ dimension.url }}">{{ dimension.dimensionlabel }}</a>
    </li>
  {% endfor %}
</ul>

## Types

<ul>
  {% for type in site.types %}
    <li>
      <a href="{{ site.baseurl }}{{ type.url }}">{{ type.locallabel }}</a>
    </li>
  {% endfor %}
</ul>