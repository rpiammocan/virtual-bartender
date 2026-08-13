import { useState } from "react";
import { api } from "../api";
import AppHeader from "../components/AppHeader";

type Props={onHome:()=>void;openRecipe?:(id:number)=>void};

export default function ImportRecipePage({onHome,openRecipe}:Props){
  const [mode,setMode]=useState<"single"|"bulk">("single");
  const [url,setUrl]=useState("");
  const [draft,setDraft]=useState<any>(null);
  const [collection,setCollection]=useState<any>(null);
  const [selected,setSelected]=useState<string[]>([]);
  const [error,setError]=useState("");
  const [busy,setBusy]=useState(false);
  const [progress,setProgress]=useState("");
  const [savedId,setSavedId]=useState<number|null>(null);

  async function importRecipe(target=url){setBusy(true);setError("");setDraft(null);setSavedId(null);try{setDraft(await api.importer.fromUrl(target))}catch(err){setError(err instanceof Error?err.message:"Import failed.")}finally{setBusy(false)}}
  async function scan(){setBusy(true);setError("");setCollection(null);try{const result=await api.importer.scanCollection(url);setCollection(result);setSelected(result.recipes.map((r:any)=>r.url))}catch(err){setError(err instanceof Error?err.message:"Collection scan failed.")}finally{setBusy(false)}}
  function updateIngredient(index:number,key:string,value:any){setDraft((current:any)=>{const ingredients=[...current.ingredients];ingredients[index]={...ingredients[index],[key]:value};return{...current,ingredients}})}
  async function saveRecipe(){setBusy(true);setError("");try{const result=await api.importer.save({source_url:draft.source_url,source_name:draft.source_name,name:draft.name,recipe_type:draft.recipe_type||"cocktail",instructions:draft.instructions||[],ingredients:draft.ingredients||[],warnings:draft.warnings||[],extraction_method:draft.extraction_method,description:null,image_path:null});setSavedId(result.recipe_id)}catch(err){setError(err instanceof Error?err.message:"Unable to save recipe.")}finally{setBusy(false)}}
  async function bulkImport(){setBusy(true);setError("");let done=0;let skipped=0;for(const target of selected){try{setProgress(`Importing ${done+skipped+1} of ${selected.length}…`);const item=await api.importer.fromUrl(target);if(item.possible_duplicates?.some((d:any)=>d.score>=95)){skipped++;continue}await api.importer.save({source_url:item.source_url,source_name:item.source_name,name:item.name,recipe_type:"cocktail",instructions:item.instructions||[],ingredients:item.ingredients||[],warnings:item.warnings||[],extraction_method:item.extraction_method,description:null,image_path:null});done++}catch{skipped++}}setProgress(`Finished: ${done} imported, ${skipped} skipped/review needed.`);setBusy(false)}

  return <main className="page theme-recipes">
    <AppHeader title="Import Recipe" onHome={onHome}/>
    <div className="theme-prop recipe-ledger"><strong>Recipe Desk</strong><span>Add your own formula or bring in recipes from the outside.</span></div>
    <div className="toolbar"><button className={mode==="single"?"primary":""} onClick={()=>setMode("single")}>Single Recipe</button><button className={mode==="bulk"?"primary":""} onClick={()=>setMode("bulk")}>Bulk Import from Website</button></div>
    <p className="lede">{mode==="single"?"Paste one recipe URL. Review and edit everything before saving it locally.":"Paste a recipe collection page. Scan it, select recipes, and save them to your offline Virtual Bartender database."}</p>
    <div className="toolbar"><input className="wide-input" placeholder="https://..." value={url} onChange={e=>setUrl(e.target.value)}/><button className="primary" disabled={busy||!url.trim()} onClick={()=>mode==="single"?importRecipe():scan()}>{busy?"Working…":mode==="single"?"Import & Review":"Scan Website"}</button></div>
    {error&&<p className="error">{error}</p>}

    {mode==="bulk"&&collection&&<section className="detail-card"><h2>{collection.count} recipes found</h2><div className="toolbar"><button onClick={()=>setSelected(collection.recipes.map((r:any)=>r.url))}>Select All</button><button onClick={()=>setSelected([])}>Clear</button><button className="primary" disabled={busy||selected.length===0} onClick={bulkImport}>Import Selected ({selected.length})</button></div><div className="result-list">{collection.recipes.map((item:any)=><label className="recipe-card" key={item.url}><span><input type="checkbox" checked={selected.includes(item.url)} onChange={e=>setSelected(current=>e.target.checked?[...current,item.url]:current.filter(x=>x!==item.url))}/> {item.name}</span><small>{item.url}</small></label>)}</div>{progress&&<p className="success">{progress}</p>}</section>}

    {mode==="single"&&draft&&<section className="detail-card"><p className="eyebrow">Review import</p><label>Recipe name<input className="wide-input" value={draft.name||""} onChange={e=>setDraft({...draft,name:e.target.value})}/></label><label> Type <select value={draft.recipe_type||"cocktail"} onChange={e=>setDraft({...draft,recipe_type:e.target.value})}><option value="cocktail">Cocktail</option><option value="mocktail">Mocktail</option></select></label><p><strong>Source:</strong> {draft.source_name}</p><h3>Ingredients</h3><div className="import-ingredients">{draft.ingredients?.map((item:any,index:number)=><div className="import-row" key={index}><input value={item.quantity??""} onChange={e=>updateIngredient(index,"quantity",e.target.value===""?null:Number(e.target.value))} placeholder="Qty"/><select value={item.unit||""} onChange={e=>updateIngredient(index,"unit",e.target.value||null)}><option value="">Unit</option><option value="oz">oz</option><option value="tsp">tsp</option><option value="tbsp">tbsp</option><option value="dash">dash</option><option value="pc">pc</option></select><input value={item.name||""} onChange={e=>updateIngredient(index,"name",e.target.value)} placeholder="Ingredient"/></div>)}</div><h3>Instructions</h3><textarea rows={8} value={(draft.instructions||[]).join("\n")} onChange={e=>setDraft({...draft,instructions:e.target.value.split("\n").filter((x:string)=>x.trim())})}/>{draft.possible_duplicates?.length>0&&<><h3>Possible duplicates</h3>{draft.possible_duplicates.map((dup:any)=><p key={dup.recipe_id}>{dup.name} — {dup.score}% match</p>)}</>}<div className="toolbar"><button className="primary" disabled={busy||!draft.name?.trim()} onClick={saveRecipe}>Save Recipe</button></div>{savedId!==null&&<p className="success">Recipe saved successfully. {openRecipe&&<button className="link-button" onClick={()=>openRecipe(savedId)}>View Recipe</button>}</p>}</section>}
  </main>;
}
