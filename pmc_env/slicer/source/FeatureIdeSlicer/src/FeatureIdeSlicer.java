import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collection;
import de.ovgu.featureide.fm.core.analysis.cnf.formula.FeatureModelFormula;
import de.ovgu.featureide.fm.core.base.IFeatureModel;
import de.ovgu.featureide.fm.core.init.FMCoreLibrary;
import de.ovgu.featureide.fm.core.init.LibraryManager;
import de.ovgu.featureide.fm.core.io.IPersistentFormat;
import de.ovgu.featureide.fm.core.io.manager.FeatureModelManager;
import de.ovgu.featureide.fm.core.io.manager.FileHandler;
import de.ovgu.featureide.fm.core.job.IJob;
import de.ovgu.featureide.fm.core.job.IJob.JobStatus;
import de.ovgu.featureide.fm.core.job.IRunner;
import de.ovgu.featureide.fm.core.job.LongRunningMethod;
import de.ovgu.featureide.fm.core.job.LongRunningWrapper;
import de.ovgu.featureide.fm.core.job.SliceFeatureModel;

public class FeatureIdeSlicer {

	public static void main(String[] args) {
		if (args.length<3) {
			throw new IllegalArgumentException("Argument count is invalid! Arguments must contain a file path, test identifier and at least one variable number.");
		}
		final String filePath = args[0];
		final String testIdentifier = args[1];
		final Collection<String> selectedFeatures = new ArrayList<String>();
		for(int i = 2; i<args.length; i++) {
	         selectedFeatures.add(args[i]);
	      }
		LibraryManager.registerLibrary(FMCoreLibrary.getInstance());
		final Path fmFile = Paths.get(filePath);
		final FileHandler<IFeatureModel> fileHandler = FeatureModelManager.getFileHandler(fmFile);
		if (fileHandler.getLastProblems().containsError()) {
			throw new IllegalArgumentException(fileHandler.getLastProblems().getErrors().get(0).error);
		}
		final IFeatureModel featureModel = new FeatureModelFormula(fileHandler.getObject()).getFeatureModel();
		if (featureModel != null) {
			final IPersistentFormat<IFeatureModel> format = fileHandler.getFormat();
			final LongRunningMethod<IFeatureModel> method = new SliceFeatureModel(featureModel, selectedFeatures, true);
			final IRunner<IFeatureModel> runner = LongRunningWrapper.getRunner(method, "Slicing Feature Model");
			runner.addJobFinishedListener(finishedJob -> save(finishedJob, fmFile, testIdentifier, format));
			runner.schedule();
		} else {
			System.out.println("Feature model could not be read!");
		}
	}
	
	private static void save(IJob<IFeatureModel> finishedJob, Path file, String testIdentifier, IPersistentFormat<IFeatureModel> format) {
		if (finishedJob.getStatus() == JobStatus.OK) {
			final Path modelFilePath = file;
			final Path fileName = modelFilePath.getFileName();
			final Path root = modelFilePath.getRoot();
			if ((fileName != null) && (root != null)) {
				String newFileName = fileName.toString();
				final int extIndex = newFileName.lastIndexOf('.');
				newFileName = ((extIndex > 0) ? newFileName.substring(0, extIndex) : newFileName) + "__" + testIdentifier + "_sliced" + "." + format.getSuffix();
				final Path newFilePath = root.resolve(modelFilePath.subpath(0, modelFilePath.getNameCount() - 2)).resolve("sliced").resolve(newFileName);
				System.out.println("Filepath: " + newFilePath.toString());
				FeatureModelManager.save(finishedJob.getResults(), newFilePath, format);
			}
		}
	}

}
