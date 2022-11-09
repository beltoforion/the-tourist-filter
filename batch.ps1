for ($i = 1; $i -lt 6; $i++)
{
	[string]$folder = [string]::Format("./stack{0}", $i)
	python ./filter-all-tourists.py -i $folder -m CUT -v ([string]::Format("./video_stack{0}_cut.mp4", $i))
	python ./filter-all-tourists.py -i $folder -m CUT_AND_MEDIAN -v ([string]::Format("./video_stack{0}_cut_and_median.mp4", $i))
	python ./filter-all-tourists.py -i $folder -m MEDIAN -v ([string]::Format("./video_stack{0}_median.mp4", $i))
	python ./filter-all-tourists.py -i $folder -m NOISE_AND_MEDIAN -v ([string]::Format("./video_stack{0}_noise.mp4", $i))
	python ./filter-all-tourists.py -i $folder -m INPAINT_AND_MEDIAN -v ([string]::Format("./video_stack{0}_inpaint.mp4", $i))
}