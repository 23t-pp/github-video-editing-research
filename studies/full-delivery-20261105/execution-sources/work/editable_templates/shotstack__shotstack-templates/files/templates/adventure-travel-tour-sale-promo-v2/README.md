# Adventure Tour & Travel Sale Promo

A video template for the Shotstack Edit API.

**Type:** Video · **Aspect:** 9:16 · **Duration:** 5s · **Format:** mp4 · **Category:** Travel

![Adventure Tour & Travel Sale Promo preview](https://d2jn8jtjz02j0j.cloudfront.net/images/origin/Adventure_Tour_and_Travel_Sale_Promo_2c2827baf4.png)

[**Preview and customise this template on shotstack.io →**](https://shotstack.io/studio/templates/adventure-travel-tour-sale-promo-v2/)

## Render a batch from the command line

`template.json` is the full [Shotstack Edit API](https://shotstack.io/docs/api/) payload. From the repo root:

```sh
npm install csv-parse
SHOTSTACK_API_KEY=your_production_key node render.mjs templates/adventure-travel-tour-sale-promo-v2
```

One video is rendered per `data.csv` row ([get a key](https://dashboard.shotstack.io/register)). For free
watermarked test renders, use a sandbox key and switch `render.mjs` from `/v1/` to `/stage/`.

## Merge fields

Each CSV column overrides the merge field of the same name; missing columns keep the default.

`data.csv` header row:

```
title_1,title_2,title_3,video,image_1,image_2,image_3,image_4,font_color,shape_color,background_color_2,audio
```

| Field | Default value |
| --- | --- |
| `Title_1` | REVIEW ON |
| `Title_2` | Tour |
| `Title_3` | GALLERY |
| `VIDEO` | https://templates.shotstack.io/adventure-travel-tour-sale-promo/b9f6e254-793d-4f80-8314-9c522ce662a6/source.mp4 |
| `IMAGE_1` | https://templates.shotstack.io/adventure-travel-tour-sale-promo/753b1e87-9a82-4899-92f9-f19221d80e98/source.png |
| `IMAGE_2` | https://templates.shotstack.io/adventure-travel-tour-sale-promo/3e156792-e942-4c29-92fc-3b8713c87a1f/source.png |
| `IMAGE_3` | https://templates.shotstack.io/adventure-travel-tour-sale-promo/9fd85c80-8724-40e5-912c-a2d5f3af8672/source.png |
| `IMAGE_4` | https://templates.shotstack.io/adventure-travel-tour-sale-promo/4171f685-7dba-4b86-acb8-4820c26a1649/source.png |
| `FONT_COLOR` | #000000 |
| `SHAPE_COLOR` | #f1d6bd |
| `BACKGROUND_COLOR_2` | #ffffff |
| `AUDIO` | https://templates.shotstack.io/adventure-travel-tour-sale-promo/ba42f218-a984-4274-b64a-612e46a3bf52/source.mp3 |

---

Also works with the [Shotstack MCP server](https://shotstack.io/docs/guide/agents/mcp-server/): give your AI assistant this folder's `template.json` and ask it to adapt the template to your data.
