import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.apache.ctakes.core.config.ConfigParameterConstants;
import org.apache.ctakes.core.cr.XmiTreeReader;
import org.apache.ctakes.core.util.DocumentIDAnnotationUtil;
import org.apache.ctakes.typesystem.type.refsem.UmlsConcept;
import org.apache.ctakes.typesystem.type.textsem.DiseaseDisorderMention;
import org.apache.ctakes.typesystem.type.textsem.IdentifiedAnnotation;
import org.apache.ctakes.typesystem.type.textsem.SignSymptomMention;
import org.apache.ctakes.utils.struct.CounterMap;
import org.apache.uima.cas.CASException;
import org.apache.uima.cas.FeatureStructure;
import org.apache.uima.collection.CollectionReader;
import org.apache.uima.fit.factory.CollectionReaderFactory;
import org.apache.uima.fit.pipeline.JCasIterator;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.apache.uima.resource.ResourceInitializationException;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.util.HashSet;
import java.util.Set;

/**
 * Created by tmill on 2/27/20.
 */
public class AnalyzeEconsults {
    public static void main(String[] args) throws ResourceInitializationException, CASException, FileNotFoundException {
        CommandLine cmd = null;
        try {
            cmd = new DefaultParser().parse(getOptions(), args);
        } catch (ParseException e) {
            e.printStackTrace();
            System.exit(-1);
        }
        String[] directories = cmd.getOptionValue('i').split(",");

        CounterMap<String> ssCounts = new CounterMap<>();
        CounterMap<String> ddCounts = new CounterMap<>();
        PrintWriter csvOut = new PrintWriter(cmd.getOptionValue('c'));
        writeCsvHeader(csvOut);

        for(String dir : directories) {
            CollectionReader reader = CollectionReaderFactory.createReader(XmiTreeReader.class,
                    ConfigParameterConstants.PARAM_INPUTDIR,
                    dir);
            for(JCasIterator casIter = new JCasIterator(reader); casIter.hasNext();){
                JCas jcas = casIter.next();
                countForType(jcas, SignSymptomMention.class, ssCounts);
                countForType(jcas, DiseaseDisorderMention.class, ddCounts);
                logCuis(jcas, csvOut);
            }
        }

        try(PrintWriter out = new PrintWriter(new File(cmd.getOptionValue('o')))) {
            printCuiCounts(ssCounts, 1, "Sign/Symptom", out);
            printCuiCounts(ddCounts, 1, "Disease/Disorder", out);
        }
        csvOut.close();
    }

    private static void writeCsvHeader(PrintWriter out){
        out.println("RowId,CUI,Polarity,Uncertainty,Generic,Historical");
    }

    private static void logCuis(JCas jcas, PrintWriter out){
        String docId = DocumentIDAnnotationUtil.getDocumentID(jcas);
        for(IdentifiedAnnotation annot: JCasUtil.select(jcas, IdentifiedAnnotation.class)){
            Set<String> reportedCuis = new HashSet<>();
            if(annot.getOntologyConceptArr() != null){
                for(FeatureStructure fs : annot.getOntologyConceptArr()){
                    if(fs instanceof UmlsConcept){
                        UmlsConcept concept = (UmlsConcept) fs;
                        String cui = concept.getCui();
                        // don't need to write 2 lines with the same CUI for the same entity mention (attributes will be all the same)
                        if(reportedCuis.contains(cui)) continue;
                        out.println(String.format("%s,%s,%d,%d,%b,%d", docId, cui, annot.getPolarity(), annot.getUncertainty(), annot.getGeneric(), annot.getHistoryOf()));
                        reportedCuis.add(cui);
                    }
                }
            }
        }
    }

    private static void printCuiCounts(CounterMap<String> map, int threshold, String label, PrintWriter out){
        for(String cui : map.keySet()) {
            if (map.get(cui) > threshold) {
                out.println(String.format("[%s] %s : %d", label, cui, map.get(cui)));
            }
        }
    }

    private static void countForType(JCas jcas, Class<? extends IdentifiedAnnotation> clazz, CounterMap<String> map){
        for(IdentifiedAnnotation annot : JCasUtil.select(jcas, clazz)){
            Set<String> mentionCuis = new HashSet<>();
            if(annot.getOntologyConceptArr() != null){
                for(FeatureStructure fs : annot.getOntologyConceptArr()){
                    if(fs instanceof UmlsConcept){
                        UmlsConcept concept = (UmlsConcept) fs;
                        String cui = concept.getCui();
                        // dont' want to count a cui twice just because it's multiple times in this same mention, that is a UMLS peculiarity, not another mention.
                        if(mentionCuis.contains(cui)) continue;
                        map.add(cui);
                    }
                }
            }
        }
    }

    private static Options getOptions(){
        Options options = new Options();

        options.addOption("i", true, "Comma-separated list of directories to process");
        options.addOption("o", true, "Where to write DD/SS counts output");
        options.addOption("c", true, "Where to write CUI csv");
        return options;
    }
}
