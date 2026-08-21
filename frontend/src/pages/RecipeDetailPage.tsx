import { useEffect,useState } from "react";
import { api } from "../api";
import AppHeader from "../components/AppHeader";
type Props={recipeId:number;onHome:()=>void};
export default function RecipeDetailPage({recipeId,onHome}:Props){
 const [recipe,setRecipe]=useState<any>(null);const [detail,setDetail]=useState<any>(null);const [metric,setMetric]=useState(false);const [favorite,setFavorite]=useState(false);const [rating,setRating]=useState("5");const [notes,setNotes]=useState("");const [editing,setEditing]=useState(false);const [edit,setEdit]=useState<any>({});
 async function load(){const [display,d]=await Promise.all([api.display.recipe(recipeId,metric),api.recipes.get(recipeId)]);setRecipe(display);setDetail(d);setFavorite(d.favorite);setEdit({name:d.name,description:d.description||"",recipe_type:d.recipe_type,instructions:d.instructions||"",image_path:d.image_path||""})}
 useEffect(()=>{load()},[recipeId,metric]);if(!recipe||!detail)return <main className="page"><p>Loading recipe…</p></main>;
 async function toggleFavorite(){favorite?await api.favorites.remove(recipe.id):await api.favorites.add(recipe.id);setFavorite(!favorite)}
 async function madeThis(){await api.history.add({recipe_id:recipe.id,rating:Number(rating),notes:notes||null});setNotes("");window.alert("Added to drink history.")}
 async function saveEdit(){await api.recipes.update(recipe.id,{...edit,source_type:detail.source_type});setEditing(false);await load()}
 async function hideRecipe(){if(!window.confirm(detail.source_type==="built_in"?"Hide this built-in recipe from your local catalog?":"Delete this recipe from your local catalog?"))return;await api.recipes.hide(recipe.id);onHome()}
 function printRecipe(){
  const printable=window.open("","_blank","popup=yes,width=760,height=900");
  if(!printable){window.print();return}
  const doc=printable.document;
  doc.open();
  doc.write('<!doctype html><html><head><title>Virtual Bartender Recipe</title><meta charset="utf-8"><style>body{font-family:Georgia,\"Times New Roman\",serif;color:#111;background:#fff;margin:0;padding:32px}main{max-width:720px;margin:0 auto}h1{text-align:center;font-size:28pt;margin:0 0 24px}h2{margin:22px 0 8px;border-bottom:1px solid #bbb;padding-bottom:5px}p,li{font-size:12pt;line-height:1.45}ul{padding-left:24px}img{display:block;max-width:100%;max-height:360px;object-fit:contain;margin:0 auto 22px}.meta{text-align:center;color:#555;margin-top:-14px;margin-bottom:22px}.no-print{margin:24px 0;text-align:center}.no-print button{font:inherit;padding:8px 14px}@media print{body{padding:0}.no-print{display:none}}</style></head><body><main id="recipe-print-root"></main></body></html>');
  doc.close();
  const root=doc.getElementById("recipe-print-root");if(!root){printable.close();window.print();return}
  const title=doc.createElement("h1");title.textContent=recipe.name;root.appendChild(title);
  if(recipe.image_path){const img=doc.createElement("img");img.src=new URL(recipe.image_path,window.location.href).href;img.alt=recipe.name;root.appendChild(img)}
  if(recipe.description){const desc=doc.createElement("p");desc.textContent=recipe.description;root.appendChild(desc)}
  const ih=doc.createElement("h2");ih.textContent="Ingredients";root.appendChild(ih);
  const list=doc.createElement("ul");recipe.ingredients.forEach((item:any)=>{const li=doc.createElement("li");li.textContent=`${item.quantity??""} ${item.unit??""} ${item.name}${item.optional?" (optional)":""}`.replace(/\s+/g," ").trim();list.appendChild(li)});root.appendChild(list);
  const sh=doc.createElement("h2");sh.textContent="Instructions";root.appendChild(sh);
  const inst=doc.createElement("p");inst.textContent=recipe.instructions||"No instructions yet.";root.appendChild(inst);
  const controls=doc.createElement("div");controls.className="no-print";const button=doc.createElement("button");button.textContent="Print";button.onclick=()=>printable.print();controls.appendChild(button);root.appendChild(controls);
  const launch=()=>{try{printable.focus();printable.print()}catch{}};
  if(recipe.image_path){const img=root.querySelector("img");if(img&&!img.complete){img.addEventListener("load",()=>setTimeout(launch,100),{once:true});img.addEventListener("error",()=>setTimeout(launch,100),{once:true});return}}
  setTimeout(launch,100);
 }
 return <main className="page"><AppHeader title={recipe.name} onHome={onHome}/><h1 className="recipe-print-title print-only">{recipe.name}</h1><div className="toolbar no-print"><button className="primary" onClick={()=>setEditing(!editing)}>✎ Edit</button><button onClick={toggleFavorite}>{favorite?"★ Favorite":"☆ Add Favorite"}</button><button onClick={()=>setMetric(!metric)}>{metric?"US Units":"Metric"}</button><button onClick={printRecipe}>Print Recipe</button><button className="danger-link" onClick={hideRecipe}>{detail.source_type==="built_in"?"Hide Recipe":"Delete Recipe"}</button></div>
 {editing&&<section className="detail-card no-print"><p className="eyebrow">Local recipe edit</p>{detail.source_type==="built_in"&&<p className="lede">This changes your local copy only; the built-in identity is preserved for future updates.</p>}<label>Name<input className="wide-input" value={edit.name} onChange={e=>setEdit({...edit,name:e.target.value})}/></label><label>Description<textarea rows={3} value={edit.description} onChange={e=>setEdit({...edit,description:e.target.value})}/></label><label>Type <select value={edit.recipe_type} onChange={e=>setEdit({...edit,recipe_type:e.target.value})}><option value="cocktail">Cocktail</option><option value="mocktail">Mocktail</option></select></label><label>Instructions<textarea rows={8} value={edit.instructions} onChange={e=>setEdit({...edit,instructions:e.target.value})}/></label><div className="toolbar"><button className="primary" onClick={saveEdit}>Save Changes</button><button onClick={()=>setEditing(false)}>Cancel</button></div></section>}
 {recipe.image_path&&<figure className="recipe-image-wrap"><img className="recipe-image" src={recipe.image_path} alt={recipe.name}/>{recipe.image_ai_generated&&<figcaption className="ai-label">AI-generated image</figcaption>}</figure>}{recipe.description&&<p className="lede">{recipe.description}</p>}<section className="detail-card"><h2>Ingredients</h2><ul>{recipe.ingredients.map((item:any)=><li key={item.ingredient_id}>{item.quantity??""} {item.unit??""} {item.name}{item.optional?" (optional)":""}</li>)}</ul></section><section className="detail-card"><h2>Instructions</h2><p>{recipe.instructions||"No instructions yet."}</p></section>
 <section className="detail-card no-print"><h2>I Made This</h2><label>Rating <select value={rating} onChange={e=>setRating(e.target.value)}>{[5,4,3,2,1].map(n=><option key={n} value={n}>{n} star{n===1?"":"s"}</option>)}</select></label><textarea value={notes} onChange={e=>setNotes(e.target.value)} placeholder="Optional notes" rows={4}/><button className="primary" onClick={madeThis}>Confirm Made</button></section></main>;
}
