import importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('ingest',Path(__file__).parents[1]/'scripts/ingest_cvm.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class IngestionTests(unittest.TestCase):
 def record(self,v):return {'CNPJ_FUNDO_CLASSE':'00.000.000/0001-00','DT_COMPTC':'2026-04-30','DENOM_SOCIAL':'Example','TP_FUNDO_CLASSE':'FIP','PL':v}
 def test_subclass_duplicates_do_not_double_count(self):
  audit=[];result=m.normalize([self.record('10'),self.record('10.0')],{'PL':'nav'},'FIP',audit);self.assertEqual(len(result),1);self.assertEqual(next(iter(result.values()))['nav'],10);self.assertEqual(audit,[])
 def test_conflict_is_excluded(self):
  audit=[];result=m.normalize([self.record('10'),self.record('12')],{'PL':'nav'},'FIP',audit);self.assertEqual(result,{});self.assertEqual(audit[0]['reason'],'conflicting_values')
 def test_missing_and_negative_remain_distinct(self):
  self.assertIsNone(m.number(''));self.assertEqual(m.number('-12'),-12)
if __name__=='__main__':unittest.main()
